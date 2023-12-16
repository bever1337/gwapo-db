-- Deploy gawpo-db:currencies to pg
BEGIN;

CREATE TABLE gwapese.currencies (
  id smallint NOT NULL,
  categories smallint[] NOT NULL,
  deprecated boolean NOT NULL,
  icon text NOT NULL,
  presentation_order smallint NOT NULL,
  CONSTRAINT currencies_PK PRIMARY KEY (id)
);

CREATE TABLE gwapese.described_currencies (
  id smallint NOT NULL,
  currency_description text,
  language_tag text NOT NULL,
  CONSTRAINT described_currencies_PK PRIMARY KEY (id, language_tag),
  CONSTRAINT described_currencies_FK_id FOREIGN KEY (id) REFERENCES
    gwapese.currencies (id) ON DELETE CASCADE,
  CONSTRAINT described_currencies_FK_language_tag FOREIGN KEY (language_tag)
    REFERENCES gwapese.language_tags (language_tag)
);

CREATE TABLE gwapese.named_currencies (
  id smallint NOT NULL,
  currency_name text,
  language_tag text NOT NULL,
  CONSTRAINT named_currencies_PK PRIMARY KEY (id, language_tag),
  CONSTRAINT named_currencies_FK_id FOREIGN KEY (id) REFERENCES
    gwapese.currencies (id) ON DELETE CASCADE,
  CONSTRAINT named_currencies_FK_language_tag FOREIGN KEY (language_tag)
    REFERENCES gwapese.language_tags (language_tag)
);

CREATE OR REPLACE FUNCTION gwapese.select_currencies (IN in_language_tag text)
  RETURNS TABLE (
    id smallint,
    categories smallint[],
    currency_description text,
    currency_name text,
    deprecated boolean,
    icon text,
    presentation_order smallint
  )
  AS $$
  SELECT
    c.id,
    c.categories,
    described_currency.currency_description,
    named_currency.currency_name,
    c.deprecated,
    c.icon,
    c.presentation_order
  FROM
    gwapese.currencies AS c
  LEFT JOIN gwapese.named_currencies AS named_currency ON named_currency.id = c.id
    AND named_currency.language_tag = in_language_tag
  LEFT JOIN gwapese.described_currencies AS described_currency ON
    described_currency.id = c.id
    AND described_currency.language_tag = in_language_tag
  ORDER BY
    c.presentation_order
$$
LANGUAGE SQL;

CREATE OR REPLACE PROCEDURE gwapese.upsert_currency (in_id smallint,
  in_categories smallint[], in_deprecated boolean, in_icon text,
  in_presentation_order smallint)
  AS $$
BEGIN
  MERGE INTO gwapese.currencies AS target_currency
  USING (
  VALUES (in_id)) AS source_currency (id) ON target_currency.id = source_currency.id
  WHEN MATCHED THEN
    UPDATE SET
      (presentation_order, icon, categories, deprecated) =
	(COALESCE(in_presentation_order, target_currency.presentation_order),
	COALESCE(in_icon, target_currency.icon), COALESCE(in_categories,
	target_currency.categories), COALESCE(in_deprecated,
	target_currency.deprecated))
  WHEN NOT MATCHED THEN
    INSERT (id, presentation_order, icon, categories, deprecated)
      VALUES (in_id, in_presentation_order, in_icon, in_categories, in_deprecated);
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE gwapese.upsert_currency_description (in_id
  smallint, in_currency_description text, in_language_tag text)
  AS $$
BEGIN
  MERGE INTO gwapese.described_currencies AS target_currency
  USING (
  VALUES (in_id, in_language_tag)) AS source_currency (id, language_tag) ON
    target_currency.id = source_currency.id
    AND target_currency.language_tag = source_currency.language_tag
  WHEN MATCHED THEN
    UPDATE SET
      currency_description = in_currency_description
  WHEN NOT MATCHED THEN
    INSERT (id, currency_description, language_tag)
      VALUES (in_id, in_currency_description, in_language_tag);
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE gwapese.upsert_currency_name (in_id smallint,
  in_currency_name text, in_language_tag text)
  AS $$
BEGIN
  MERGE INTO gwapese.named_currencies AS target_currency
  USING (
  VALUES (in_id, in_language_tag)) AS source_currency (id, language_tag) ON
    target_currency.id = source_currency.id
    AND target_currency.language_tag = source_currency.language_tag
  WHEN MATCHED THEN
    UPDATE SET
      currency_name = in_currency_name
  WHEN NOT MATCHED THEN
    INSERT (id, currency_name, language_tag)
      VALUES (in_id, in_currency_name, in_language_tag);
END;
$$
LANGUAGE plpgsql;

COMMIT;
