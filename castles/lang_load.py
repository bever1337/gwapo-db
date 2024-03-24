import luigi
from os import path
from psycopg import sql

import common
from tasks import config
from tasks import load_csv


class LangLoad(luigi.Task):
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "lang"

    def output(self):
        gwapo_config = config.gconfig()
        return luigi.LocalTarget(
            path=path.join(
                str(gwapo_config.output_dir),
                self.get_task_family(),
                path.extsep.join([self.task_id, "txt"]),
            )
        )

    def run(self):
        with (
            common.get_conn() as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(query="BEGIN")
            try:
                cursor.execute(
                    query="""
MERGE INTO gwapese.lang AS target_lang
USING (
  SELECT
    lang_tag
  FROM
    unnest(%(lang_tags)s::text[]) AS lang_tag) AS source_lang ON
      target_lang.lang_tag = source_lang.lang_tag
WHEN NOT MATCHED THEN
  INSERT (lang_tag)
    VALUES (source_lang.lang_tag);
""",
                    params={
                        "lang_tags": [known_lang.value for known_lang in common.LangTag]
                    },
                )

                cursor.execute(
                    query=sql.SQL(
                        """
MERGE INTO gwapese.app AS target_app
USING (
  VALUES (%(app_name)s::text)) AS source_app (app_name) ON target_app.app_name =
    source_app.app_name
  WHEN NOT MATCHED THEN
    INSERT (app_name)
      VALUES (source_app.app_name);
"""
                    ),
                    params={"app_name": "gw2"},
                )
                cursor.execute(
                    query=sql.SQL(
                        """
MERGE INTO gwapese.operating_lang AS target_operating_lang
USING (
  VALUES (%(app_name)s::text, %(lang_tag)s::text)) AS source_operating_lang (app_name, lang_tag)
  ON target_operating_lang.app_name = source_operating_lang.app_name
  AND target_operating_lang.lang_tag = source_operating_lang.lang_tag
WHEN NOT MATCHED THEN
  INSERT (app_name, lang_tag)
    VALUES (source_operating_lang.app_name, source_operating_lang.lang_tag);
"""
                    ),
                    params={"app_name": "gw2", "lang_tag": "en"},
                )

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output_file:
                    w_output_file.write("ok")
            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


class LangLoadCopySourceTask(load_csv.LoadCsvTask):
    app_name = luigi.Parameter(default="gw2")
    id_attributes: list[tuple[str, sql.SQL]]
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    @property
    def precopy_sql(self):
        temp_table_name = sql.Identifier("_".join(["tempo", str(self.table)]))
        return sql.Composed(
            [
                sql.SQL(
                    """
CREATE TEMPORARY TABLE {temp_table_name} (
  LIKE gwapese.copy_source
) ON COMMIT DROP;
"""
                ).format(temp_table_name=temp_table_name),
                sql.Composed(
                    [
                        sql.SQL("ALTER TABLE {temp_table_name} ").format(
                            temp_table_name=temp_table_name
                        ),
                        sql.SQL(", ").join(
                            [
                                *[
                                    sql.SQL(
                                        "ADD COLUMN IF NOT EXISTS {attribute} {attribute_type}"
                                    ).format(
                                        attribute=sql.Identifier(attribute),
                                        attribute_type=attribute_type,
                                    )
                                    for (
                                        attribute,
                                        attribute_type,
                                    ) in self.id_attributes
                                ],
                                sql.SQL("DROP COLUMN IF EXISTS sysrange_lower"),
                                sql.SQL("DROP COLUMN IF EXISTS sysrange_upper"),
                            ]
                        ),
                        sql.SQL(";"),
                    ]
                ),
            ]
        )

    @property
    def postcopy_sql(self):
        temp_table_name = sql.Identifier("_".join(["tempo", str(self.table)]))
        return sql.Composed(
            [
                *[
                    (
                        sql.SQL(
                            """
MERGE INTO gwapese.{table_name} AS target_copy_source
USING (
  SELECT DISTINCT ON (
    app_name,
    lang_tag,
    original
  )
    app_name,
    lang_tag,
    original
  FROM
    {temp_table_name}) AS source_copy_source
  ON target_copy_source.app_name = source_copy_source.app_name
  AND target_copy_source.lang_tag = source_copy_source.lang_tag
  AND target_copy_source.original = source_copy_source.original
WHEN NOT MATCHED THEN
  INSERT (app_name, lang_tag, original)
    VALUES (source_copy_source.app_name, source_copy_source.lang_tag,
      source_copy_source.original);
"""
                        ).format(
                            table_name=sql.Identifier(table_name),
                            temp_table_name=temp_table_name,
                        )
                    )
                    for table_name in ["copy_document", "copy_source"]
                ],
                sql.Composed(
                    [
                        sql.SQL(
                            """
MERGE INTO gwapese.{table_name} AS target_copy_widget
USING {temp_table_name} AS source_copy_widget
  ON
"""
                        ).format(
                            table_name=sql.Identifier(str(self.table)),
                            temp_table_name=temp_table_name,
                        ),
                        sql.SQL(" AND ").join(
                            [
                                sql.SQL(
                                    " target_copy_widget.{key} = source_copy_widget.{key} "
                                ).format(key=sql.Identifier(id_attribute))
                                for id_attribute in [
                                    "app_name",
                                    "lang_tag",
                                    *[
                                        attribute
                                        for [attribute, _] in self.id_attributes
                                    ],
                                ]
                            ]
                        ),
                        sql.SQL(
                            """
WHEN MATCHED AND target_copy_widget.original != source_copy_widget.original THEN
  UPDATE SET
    original = source_copy_widget.original
WHEN NOT MATCHED THEN
  INSERT (
"""
                        ),
                        sql.SQL(", ").join(
                            [
                                sql.Identifier(id_attribute)
                                for id_attribute in [
                                    "app_name",
                                    "lang_tag",
                                    "original",
                                    *[
                                        attribute
                                        for [attribute, _] in self.id_attributes
                                    ],
                                ]
                            ]
                        ),
                        sql.SQL(") VALUES ("),
                        sql.SQL(", ").join(
                            [
                                sql.SQL(".").join(
                                    [
                                        sql.Identifier("source_copy_widget"),
                                        sql.Identifier(id_attribute),
                                    ]
                                )
                                for id_attribute in [
                                    "app_name",
                                    "lang_tag",
                                    "original",
                                    *[
                                        attribute
                                        for [attribute, _] in self.id_attributes
                                    ],
                                ]
                            ]
                        ),
                        sql.SQL(");"),
                    ]
                ),
            ]
        )


class LangLoadCopyTargetTask(load_csv.LoadCsvTask):
    app_name = luigi.Parameter(default="gw2")
    id_attributes: list[tuple[str, sql.SQL]]
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    translation_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    widget_table = luigi.Parameter()

    @property
    def precopy_sql(self):
        temp_widget_context_table = sql.Identifier("_".join(["tempo", str(self.table)]))
        return sql.Composed(
            [
                sql.SQL(
                    """
CREATE TEMPORARY TABLE {temp_widget_context_table} (
  LIKE gwapese.copy_target
) ON COMMIT DROP;
"""
                ).format(temp_widget_context_table=temp_widget_context_table),
                sql.Composed(
                    [
                        sql.SQL("ALTER TABLE {temp_widget_context_table} ").format(
                            temp_widget_context_table=temp_widget_context_table
                        ),
                        sql.SQL(", ").join(
                            [
                                *[
                                    sql.SQL(
                                        "ADD COLUMN IF NOT EXISTS {attribute} {attribute_type}"
                                    ).format(
                                        attribute=sql.Identifier(attribute),
                                        attribute_type=attribute_type,
                                    )
                                    for (
                                        attribute,
                                        attribute_type,
                                    ) in self.id_attributes
                                ],
                                sql.SQL("DROP COLUMN IF EXISTS original"),
                                sql.SQL("DROP COLUMN IF EXISTS sysrange_lower"),
                                sql.SQL("DROP COLUMN IF EXISTS sysrange_upper"),
                            ]
                        ),
                        sql.SQL(";"),
                    ]
                ),
            ]
        )

    @property
    def postcopy_sql(self):
        widget_table = sql.Identifier(str(self.widget_table))
        widget_context_table = sql.Identifier(str(self.table))
        temp_widget_context_table = sql.Identifier("_".join(["tempo", str(self.table)]))
        return sql.Composed(
            [
                sql.SQL(
                    """
MERGE INTO gwapese.copy_document AS copy_document_target
USING (
  SELECT DISTINCT ON (
    app_name,
    translation_lang_tag,
    "translation"
  )
    app_name,
    translation_lang_tag,
    "translation"
  FROM
    {temp_widget_context_table}) as copy_document_source
  ON copy_document_target.app_name = copy_document_source.app_name
  AND copy_document_target.lang_tag = copy_document_source.translation_lang_tag
  AND copy_document_target.original = copy_document_source."translation"
WHEN NOT MATCHED THEN
  INSERT (app_name, lang_tag, original)
    VALUES (copy_document_source.app_name,
      copy_document_source.translation_lang_tag,
      copy_document_source."translation");
"""
                ).format(temp_widget_context_table=temp_widget_context_table),
                sql.Composed(
                    [
                        sql.SQL(
                            """
MERGE INTO gwapese.copy_target AS target_copy_target
USING (
  SELECT DISTINCT ON (
    {temp_widget_context_table}.app_name,
    {temp_widget_context_table}.original_lang_tag,
    gwapese.{widget_table}.original,
    {temp_widget_context_table}.translation_lang_tag,
    {temp_widget_context_table}."translation"
  )
    {temp_widget_context_table}.app_name,
    {temp_widget_context_table}.original_lang_tag,
    gwapese.{widget_table}.original,
    {temp_widget_context_table}.translation_lang_tag,
    {temp_widget_context_table}."translation"
  FROM
    {temp_widget_context_table}
  INNER JOIN
    gwapese.{widget_table}
  ON
    {temp_widget_context_table}.app_name = gwapese.{widget_table}.app_name
    AND {temp_widget_context_table}.original_lang_tag = gwapese.{widget_table}.lang_tag
    AND """
                        ).format(
                            temp_widget_context_table=temp_widget_context_table,
                            widget_table=widget_table,
                        ),
                        sql.SQL(" AND ").join(
                            [
                                (
                                    sql.SQL(
                                        " {temp_widget_context_table}.{key} = gwapese.{widget_table}.{key} "
                                    ).format(
                                        key=sql.Identifier(id_attribute),
                                        temp_widget_context_table=temp_widget_context_table,
                                        widget_table=widget_table,
                                    )
                                )
                                for [id_attribute, _] in self.id_attributes
                            ]
                        ),
                        sql.SQL(
                            """
  ) AS source_copy_target
  ON target_copy_target.app_name = source_copy_target.app_name
  AND target_copy_target.original_lang_tag = source_copy_target.original_lang_tag
  AND target_copy_target.original = source_copy_target.original
  AND target_copy_target.translation_lang_tag = source_copy_target.translation_lang_tag
  AND target_copy_target."translation" = source_copy_target."translation"
WHEN NOT MATCHED THEN
  INSERT (app_name, original_lang_tag, original, translation_lang_tag, "translation")
    VALUES (
      source_copy_target.app_name,
      source_copy_target.original_lang_tag,
      source_copy_target.original,
      source_copy_target.translation_lang_tag,
      source_copy_target."translation");
"""
                        ),
                    ]
                ),
                sql.Composed(
                    [
                        sql.SQL(
                            """
MERGE INTO gwapese.{widget_context_table} AS widget_context_target
USING (
  SELECT
    {temp_widget_context_table}.app_name,
    {temp_widget_context_table}.original_lang_tag,
    gwapese.{widget_table}.original,
    {temp_widget_context_table}.translation_lang_tag,
    {temp_widget_context_table}."translation",
"""
                        ).format(
                            temp_widget_context_table=temp_widget_context_table,
                            widget_table=widget_table,
                            widget_context_table=widget_context_table,
                        ),
                        # select dynamic ID attributes
                        sql.SQL(", ").join(
                            [
                                (
                                    sql.SQL(
                                        " {temp_widget_context_table}.{key} "
                                    ).format(
                                        key=sql.Identifier(id_attribute),
                                        temp_widget_context_table=temp_widget_context_table,
                                    )
                                )
                                for [id_attribute, _] in self.id_attributes
                            ]
                        ),
                        sql.SQL(
                            """
  FROM
    {temp_widget_context_table}
  INNER JOIN
    gwapese.{widget_table}
  ON
    {temp_widget_context_table}.app_name = gwapese.{widget_table}.app_name
    AND {temp_widget_context_table}.original_lang_tag = gwapese.{widget_table}.lang_tag
    AND """
                        ).format(
                            temp_widget_context_table=temp_widget_context_table,
                            widget_table=widget_table,
                        ),
                        # join on conditions
                        sql.SQL(" AND ").join(
                            [
                                (
                                    sql.SQL(
                                        " {temp_widget_context_table}.{key} = gwapese.{widget_table}.{key} "
                                    ).format(
                                        key=sql.Identifier(id_attribute),
                                        temp_widget_context_table=temp_widget_context_table,
                                        widget_table=widget_table,
                                    )
                                )
                                for [id_attribute, _] in self.id_attributes
                            ]
                        ),
                        sql.SQL(
                            """
) AS source_copy_widget_ctx
  ON widget_context_target.app_name = source_copy_widget_ctx.app_name
  AND widget_context_target.original_lang_tag = source_copy_widget_ctx.original_lang_tag
  AND widget_context_target.original = source_copy_widget_ctx.original
  AND widget_context_target.translation_lang_tag = source_copy_widget_ctx.translation_lang_tag
  AND widget_context_target."translation" = source_copy_widget_ctx."translation"
  AND """
                        ),
                        sql.SQL(" AND ").join(
                            [
                                (
                                    sql.SQL(
                                        " widget_context_target.{key} = source_copy_widget_ctx.{key} "
                                    ).format(key=sql.Identifier(id_attribute))
                                )
                                for [id_attribute, _] in self.id_attributes
                            ]
                        ),
                        sql.SQL(
                            """
WHEN NOT MATCHED THEN
  INSERT (
    app_name,
    original_lang_tag,
    original,
    translation_lang_tag,
    "translation", """
                        ),
                        sql.SQL(", ").join(
                            [
                                sql.Identifier(id_attribute)
                                for [id_attribute, _] in self.id_attributes
                            ]
                        ),
                        sql.SQL(
                            """
  ) VALUES (
      source_copy_widget_ctx.app_name,
      source_copy_widget_ctx.original_lang_tag,
      source_copy_widget_ctx.original,
      source_copy_widget_ctx.translation_lang_tag,
      source_copy_widget_ctx."translation", """
                        ),
                        sql.SQL(", ").join(
                            [
                                sql.SQL("source_copy_widget_ctx.{key}").format(
                                    key=sql.Identifier(id_attribute)
                                )
                                for [id_attribute, _] in self.id_attributes
                            ]
                        ),
                        sql.SQL(");"),
                    ]
                ),
            ]
        )
