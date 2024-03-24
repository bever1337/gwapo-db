-- Deploy gwapo-db:item_lang to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: item
BEGIN;

CREATE TABLE gwapese.item_description (
  LIKE gwapese.copy_source,
  item_id integer NOT NULL,
  CONSTRAINT item_description_pk PRIMARY KEY (app_name, lang_tag, original, item_id),
  CONSTRAINT item_description_u UNIQUE (app_name, lang_tag, item_id),
  CONSTRAINT item_identifies_description_fk FOREIGN KEY (item_id) REFERENCES
    gwapese.item (item_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_source_identifies_item_description_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.copy_source (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.item_description_history (
  LIKE gwapese.item_description
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'item_description', 'item_description_history');

CREATE TABLE gwapese.item_description_context (
  LIKE gwapese.copy_target,
  item_id integer NOT NULL,
  CONSTRAINT item_description_context_pk PRIMARY KEY (app_name,
    original_lang_tag, translation_lang_tag, item_id),
  CONSTRAINT item_description_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, original, item_id) REFERENCES gwapese.item_description
    (app_name, lang_tag, original, item_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT copy_target_identifies_item_description_context_fk FOREIGN KEY
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    REFERENCES gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.item_description_context_history (
  LIKE gwapese.item_description_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'item_description_context', 'item_description_context_history');

CREATE TABLE gwapese.item_name (
  LIKE gwapese.copy_source,
  item_id integer NOT NULL,
  CONSTRAINT item_name_pk PRIMARY KEY (app_name, lang_tag, original, item_id),
  CONSTRAINT item_name_u UNIQUE (app_name, lang_tag, item_id),
  CONSTRAINT item_identifies_name_fk FOREIGN KEY (item_id) REFERENCES
    gwapese.item (item_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_source_identifies_item_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.copy_source (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.item_name_history (
  LIKE gwapese.item_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'item_name', 'item_name_history');

CREATE TABLE gwapese.item_name_context (
  LIKE gwapese.copy_target,
  item_id integer NOT NULL,
  CONSTRAINT item_name_context_pk PRIMARY KEY (app_name, original_lang_tag,
    translation_lang_tag, item_id),
  CONSTRAINT item_name_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, original, item_id) REFERENCES gwapese.item_name
    (app_name, lang_tag, original, item_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT copy_target_identifies_item_name_context_fk FOREIGN KEY (app_name,
    original_lang_tag, original, translation_lang_tag, translation) REFERENCES
    gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.item_name_context_history (
  LIKE gwapese.item_name_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'item_name_context', 'item_name_context_history');

COMMIT;
