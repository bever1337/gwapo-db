-- Deploy gwapo-db:mount_lang to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: mount
BEGIN;

CREATE TABLE gwapese.mount_name (
  LIKE gwapese.copy_source,
  mount_id text NOT NULL,
  CONSTRAINT mount_name_pk PRIMARY KEY (app_name, lang_tag, mount_id),
  CONSTRAINT mount_identifies_name_fk FOREIGN KEY (mount_id) REFERENCES
    gwapese.mount (mount_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_source_identifies_mount_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.copy_source (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.mount_name_history (
  LIKE gwapese.mount_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mount_name', 'mount_name_history');

CREATE TABLE gwapese.mount_name_context (
  LIKE gwapese.copy_target,
  mount_id text NOT NULL,
  CONSTRAINT mount_name_context_pk PRIMARY KEY (app_name, original_lang_tag,
    mount_id, translation_lang_tag),
  CONSTRAINT mount_name_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, mount_id) REFERENCES gwapese.mount_name (app_name,
    lang_tag, mount_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_target_identifies_mount_name_context_fk FOREIGN KEY
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    REFERENCES gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.mount_name_context_history (
  LIKE gwapese.mount_name_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mount_name_context', 'mount_name_context_history');

COMMIT;
