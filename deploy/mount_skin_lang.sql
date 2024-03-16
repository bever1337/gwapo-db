-- Deploy gwapo-db:mount_skin_lang to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: mount_skin
BEGIN;

CREATE TABLE gwapese.mount_skin_name (
  LIKE gwapese.copy_source,
  mount_skin_id integer NOT NULL,
  CONSTRAINT mount_skin_name_pk PRIMARY KEY (app_name, lang_tag, original, mount_skin_id),
  CONSTRAINT mount_skin_name_u UNIQUE (app_name, lang_tag, mount_skin_id),
  CONSTRAINT mount_skin_identifies_name_fk FOREIGN KEY (mount_skin_id)
    REFERENCES gwapese.mount_skin (mount_skin_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT copy_source_identifies_mount_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.copy_source (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.mount_skin_name_history (
  LIKE gwapese.mount_skin_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mount_skin_name', 'mount_skin_name_history');

CREATE TABLE gwapese.mount_skin_name_context (
  LIKE gwapese.copy_target,
  mount_skin_id integer NOT NULL,
  CONSTRAINT mount_skin_name_context_pk PRIMARY KEY (app_name,
    original_lang_tag, translation_lang_tag, mount_skin_id),
  CONSTRAINT mount_skin_name_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, original, mount_skin_id) REFERENCES
    gwapese.mount_skin_name (app_name, lang_tag, original, mount_skin_id) ON
    DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_target_identifies_mount_skin_name_context_fk FOREIGN KEY
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    REFERENCES gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.mount_skin_name_context_history (
  LIKE gwapese.mount_skin_name_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mount_skin_name_context', 'mount_skin_name_context_history');

COMMIT;
