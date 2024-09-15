-- Deploy gwapo-db:guild_upgrade_lang to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: guild_upgrade
BEGIN;

CREATE TABLE gwapese.guild_upgrade_description (
  LIKE gwapese.copy_source,
  guild_upgrade_id integer NOT NULL,
  CONSTRAINT guild_upgrade_description_pk PRIMARY KEY (app_name, lang_tag,
    guild_upgrade_id),
  CONSTRAINT guild_upgrade_identifies_description_fk FOREIGN KEY
    (guild_upgrade_id) REFERENCES gwapese.guild_upgrade (guild_upgrade_id) ON
    DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_source_identifies_guild_upgrade_description_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.copy_source (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.guild_upgrade_description_history (
  LIKE gwapese.guild_upgrade_description
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'guild_upgrade_description', 'guild_upgrade_description_history');

CREATE TABLE gwapese.guild_upgrade_description_context (
  LIKE gwapese.copy_target,
  guild_upgrade_id integer NOT NULL,
  CONSTRAINT guild_upgrade_description_context_pk PRIMARY KEY (app_name,
    original_lang_tag, guild_upgrade_id, translation_lang_tag),
  CONSTRAINT guild_upgrade_description_sources_context_fk FOREIGN KEY
    (app_name, original_lang_tag, guild_upgrade_id) REFERENCES
    gwapese.guild_upgrade_description (app_name, lang_tag, guild_upgrade_id) ON
    DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_target_identifies_guild_upgrade_description_context_fk
    FOREIGN KEY (app_name, original_lang_tag, original, translation_lang_tag,
    translation) REFERENCES gwapese.copy_target (app_name, original_lang_tag,
    original, translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE
    CASCADE
);

CREATE TABLE gwapese.guild_upgrade_description_context_history (
  LIKE gwapese.guild_upgrade_description_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'guild_upgrade_description_context', 'guild_upgrade_description_context_history');

CREATE TABLE gwapese.guild_upgrade_name (
  LIKE gwapese.copy_source,
  guild_upgrade_id integer NOT NULL,
  CONSTRAINT guild_upgrade_name_pk PRIMARY KEY (app_name, lang_tag, guild_upgrade_id),
  CONSTRAINT guild_upgrade_identifies_name_fk FOREIGN KEY (guild_upgrade_id)
    REFERENCES gwapese.guild_upgrade (guild_upgrade_id) ON DELETE CASCADE ON
    UPDATE CASCADE,
  CONSTRAINT copy_source_identifies_guild_upgrade_name_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.copy_source (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.guild_upgrade_name_history (
  LIKE gwapese.guild_upgrade_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'guild_upgrade_name', 'guild_upgrade_name_history');

CREATE TABLE gwapese.guild_upgrade_name_context (
  LIKE gwapese.copy_target,
  guild_upgrade_id integer NOT NULL,
  CONSTRAINT guild_upgrade_name_context_pk PRIMARY KEY (app_name,
    original_lang_tag, guild_upgrade_id, translation_lang_tag),
  CONSTRAINT guild_upgrade_name_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, guild_upgrade_id) REFERENCES gwapese.guild_upgrade_name
    (app_name, lang_tag, guild_upgrade_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_target_identifies_guild_upgrade_name_context_fk FOREIGN KEY
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    REFERENCES gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.guild_upgrade_name_context_history (
  LIKE gwapese.guild_upgrade_name_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'guild_upgrade_name_context', 'guild_upgrade_name_context_history');

COMMIT;
