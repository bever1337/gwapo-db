-- Deploy gwapo-db:skin_lang to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: skin
BEGIN;

CREATE TABLE gwapese.skin_description (
  LIKE gwapese.copy_source,
  skin_id integer NOT NULL,
  CONSTRAINT skin_description_pk PRIMARY KEY (app_name, lang_tag, original, skin_id),
  CONSTRAINT skin_description_u UNIQUE (app_name, lang_tag, skin_id),
  CONSTRAINT copy_source_identifies_skin_description_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.copy_source (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT skin_identifies_description_fk FOREIGN KEY (skin_id) REFERENCES
    gwapese.skin (skin_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.skin_description_history (
  LIKE gwapese.skin_description
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_description', 'skin_description_history');

CREATE TABLE gwapese.skin_description_context (
  LIKE gwapese.copy_target,
  skin_id integer NOT NULL,
  CONSTRAINT skin_description_context_pk PRIMARY KEY (app_name,
    original_lang_tag, translation_lang_tag, skin_id),
  CONSTRAINT skin_description_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, original, skin_id) REFERENCES gwapese.skin_description
    (app_name, lang_tag, original, skin_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT copy_target_identifies_skin_description_context_fk FOREIGN KEY
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    REFERENCES gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.skin_description_context_history (
  LIKE gwapese.skin_description_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_description_context', 'skin_description_context_history');

CREATE TABLE gwapese.skin_name (
  LIKE gwapese.copy_source,
  skin_id integer NOT NULL,
  CONSTRAINT skin_name_pk PRIMARY KEY (app_name, lang_tag, original, skin_id),
  CONSTRAINT skin_name_u UNIQUE (app_name, lang_tag, skin_id),
  CONSTRAINT copy_source_identifies_name_fk FOREIGN KEY (app_name, lang_tag,
    original) REFERENCES gwapese.copy_source (app_name, lang_tag, original) ON
    DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT skin_identifies_skin_name_fk FOREIGN KEY (skin_id) REFERENCES
    gwapese.skin (skin_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.skin_name_history (
  LIKE gwapese.skin_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_name', 'skin_name_history');

CREATE TABLE gwapese.skin_name_context (
  LIKE gwapese.copy_target,
  skin_id integer NOT NULL,
  CONSTRAINT skin_name_context_pk PRIMARY KEY (app_name, original_lang_tag,
    translation_lang_tag, skin_id),
  CONSTRAINT skin_name_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, original, skin_id) REFERENCES gwapese.skin_name
    (app_name, lang_tag, original, skin_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT copy_target_identifies_skin_name_context_fk FOREIGN KEY (app_name,
    original_lang_tag, original, translation_lang_tag, translation) REFERENCES
    gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.skin_name_context_history (
  LIKE gwapese.skin_name_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_name_context', 'skin_name_context_history');

COMMIT;
