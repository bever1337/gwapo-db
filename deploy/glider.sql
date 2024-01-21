-- Deploy gawpo-db:glider to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: color
BEGIN;

CREATE TABLE gwapese.glider (
  glider_id smallint NOT NULL,
  icon text NOT NULL,
  presentation_order smallint NOT NULL,
  CONSTRAINT glider_pk PRIMARY KEY (glider_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'glider');

CREATE TABLE gwapese.glider_history (
  LIKE gwapese.glider
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'glider', 'glider_history');

CREATE TABLE gwapese.glider_description (
  app_name text NOT NULL,
  lang_tag text NOT NULL,
  glider_id smallint NOT NULL,
  original text NOT NULL,
  CONSTRAINT glider_description_pk PRIMARY KEY (app_name, lang_tag, glider_id),
  CONSTRAINT glider_identifies_glider_description_fk FOREIGN KEY (glider_id)
    REFERENCES gwapese.glider (glider_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT operating_copy_precedes_glider_description_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.operating_copy (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE RESTRICT
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'glider_description');

CREATE TABLE gwapese.glider_description_history (
  LIKE gwapese.glider_description
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'glider_description', 'glider_description_history');

CREATE TABLE gwapese.glider_dye (
  color_id smallint NOT NULL,
  glider_id smallint NOT NULL,
  CONSTRAINT glider_dye_pk PRIMARY KEY (glider_id, color_id),
  CONSTRAINT color_identifies_glider_dye_fk FOREIGN KEY (color_id) REFERENCES
    gwapese.color (color_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT glider_identifies_glider_dye_fk FOREIGN KEY (glider_id) REFERENCES
    gwapese.glider (glider_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'glider_dye');

CREATE TABLE gwapese.glider_dye_history (
  LIKE gwapese.glider_dye
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'glider_dye', 'glider_dye_history');

CREATE TABLE gwapese.glider_name (
  app_name text NOT NULL,
  lang_tag text NOT NULL,
  glider_id smallint NOT NULL,
  original text NOT NULL,
  CONSTRAINT glider_name_pk PRIMARY KEY (app_name, lang_tag, glider_id),
  CONSTRAINT glider_identifies_glider_name_fk FOREIGN KEY (glider_id)
    REFERENCES gwapese.glider (glider_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT operating_copy_precedes_glider_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.operating_copy (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE RESTRICT
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'glider_name');

CREATE TABLE gwapese.glider_name_history (
  LIKE gwapese.glider_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'glider_name', 'glider_name_history');

COMMIT;
