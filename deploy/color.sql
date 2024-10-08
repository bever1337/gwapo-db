-- Deploy gwapo-db:color to pg
-- requires: schema
-- requires: history
BEGIN;

CREATE TABLE gwapese.color_hue (
  hue text,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT color_hue_pk PRIMARY KEY (hue)
);

CREATE TABLE gwapese.color_hue_history (
  LIKE gwapese.color_hue
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'color_hue', 'color_hue_history');

CREATE TABLE gwapese.color_material (
  material text,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT color_material_pk PRIMARY KEY (material)
);

CREATE TABLE gwapese.color_material_history (
  LIKE gwapese.color_material
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'color_material', 'color_material_history');

CREATE TABLE gwapese.color_rarity (
  rarity text,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT color_rarity_pk PRIMARY KEY (rarity)
);

CREATE TABLE gwapese.color_rarity_history (
  LIKE gwapese.color_rarity
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'color_rarity', 'color_rarity_history');

CREATE TABLE gwapese.color (
  color_id integer NOT NULL,
  hue text,
  material text,
  rarity text,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT color_pk PRIMARY KEY (color_id),
  CONSTRAINT color_hue_identifies_color_fk FOREIGN KEY (hue) REFERENCES
    gwapese.color_hue (hue) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT color_material_identifies_color_fk FOREIGN KEY (material)
    REFERENCES gwapese.color_material (material) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT color_rarity_identifies_color_fk FOREIGN KEY (rarity) REFERENCES
    gwapese.color_rarity (rarity) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.color_history (
  LIKE gwapese.color
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'color', 'color_history');

CREATE TABLE gwapese.color_base (
  blue smallint NOT NULL,
  color_id integer NOT NULL,
  green smallint NOT NULL,
  red smallint NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT color_base_pk PRIMARY KEY (color_id),
  CONSTRAINT color_identifies_base_fk FOREIGN KEY (color_id) REFERENCES
    gwapese.color (color_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.color_base_history (
  LIKE gwapese.color_base
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'color_base', 'color_base_history');

-- todo should material be normalized? All (but 2) dyes have all 4 materials
CREATE TABLE gwapese.color_sample (
  color_id integer NOT NULL,
  material text NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT color_sample_pk PRIMARY KEY (color_id, material),
  CONSTRAINT color_comprises_sample_fk FOREIGN KEY (color_id) REFERENCES
    gwapese.color (color_id) ON DELETE CASCADE
);

CREATE TABLE gwapese.color_sample_history (
  LIKE gwapese.color_sample
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'color_sample', 'color_sample_history');

CREATE TABLE gwapese.color_sample_adjustment (
  brightness smallint NOT NULL,
  color_id integer NOT NULL,
  contrast double precision NOT NULL,
  material text NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT color_sample_adjustment_pk PRIMARY KEY (color_id, material),
  CONSTRAINT color_sample_identifies_adjustment_fk FOREIGN KEY (color_id,
    material) REFERENCES gwapese.color_sample (color_id, material) ON DELETE
    CASCADE
);

CREATE TABLE gwapese.color_sample_adjustment_history (
  LIKE gwapese.color_sample_adjustment
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'color_sample_adjustment', 'color_sample_adjustment_history');

CREATE TABLE gwapese.color_sample_shift (
  color_id integer NOT NULL,
  hue smallint NOT NULL,
  lightness double precision NOT NULL,
  material text NOT NULL,
  saturation double precision NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT color_sample_shift_pk PRIMARY KEY (color_id, material),
  CONSTRAINT color_sample_identifies_shift_fk FOREIGN KEY (color_id, material)
    REFERENCES gwapese.color_sample (color_id, material) ON DELETE CASCADE
);

CREATE TABLE gwapese.color_sample_shift_history (
  LIKE gwapese.color_sample_shift
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'color_sample_shift', 'color_sample_shift_history');

CREATE TABLE gwapese.color_sample_reference (
  blue smallint NOT NULL,
  color_id integer NOT NULL,
  green smallint NOT NULL,
  material text NOT NULL,
  red smallint NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT color_sample_reference_pk PRIMARY KEY (color_id, material),
  CONSTRAINT color_sample_reference_u UNIQUE (color_id, material, red, green, blue),
  CONSTRAINT color_sample_identifies_reference_fk FOREIGN KEY (color_id,
    material) REFERENCES gwapese.color_sample (color_id, material) ON DELETE
    CASCADE
);

CREATE TABLE gwapese.color_sample_reference_history (
  LIKE gwapese.color_sample_reference
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'color_sample_reference', 'color_sample_reference_history');

CREATE OR REPLACE FUNCTION gwapese.rgb_to_hex (IN in_red smallint, IN in_green
  smallint, IN in_blue smallint)
  RETURNS varchar (
    6
)
  AS $$
BEGIN
  RETURN lpad(lpad(to_hex(cast(in_red AS int)), 2, '0') ||
    lpad(to_hex(cast(in_green AS int)), 2, '0') ||
    lpad(to_hex(cast(in_blue AS int)), 2, '0'), 6,
    '0');
END;
$$
LANGUAGE plpgsql
IMMUTABLE;

CREATE OR REPLACE FUNCTION gwapese.srgb_to_lin (IN in_color_channel double precision)
  RETURNS double precision
  AS $$
BEGIN
  CASE WHEN in_color_channel <= 0.04045 THEN
    RETURN in_color_channel / 12.92;
  ELSE
    RETURN power((in_color_channel + 0.055) / 1.055, 2.4);
  END CASE;
END;
$$
LANGUAGE plpgsql
IMMUTABLE;

CREATE OR REPLACE FUNCTION gwapese.rgb_to_y (IN in_red double precision, IN
  in_green double precision, IN in_blue double precision)
  RETURNS double precision
  AS $$
BEGIN
  RETURN 0.2126 * (
    SELECT
      gwapese.srgb_to_lin (in_red) AS red_linear) + 0.7152 * (
    SELECT
      gwapese.srgb_to_lin (in_green) AS green_linear) + 0.0722 * (
    SELECT
      gwapese.srgb_to_lin (in_blue) AS blue_linear);
END;
$$
LANGUAGE plpgsql
IMMUTABLE;

CREATE OR REPLACE FUNCTION gwapese.y_to_lstar (IN in_y double precision)
  RETURNS double precision
  AS $$
BEGIN
  CASE WHEN in_y <= (216.0 / 24389.0) THEN
    RETURN in_y * (24389.0 / 27.0);
  ELSE
    RETURN power(in_y, (1.0 / 3.0)) * 116 - 16;
  END CASE;
END;
$$
LANGUAGE plpgsql
IMMUTABLE;

CREATE OR REPLACE FUNCTION gwapese.rgb_to_lightness (IN in_red smallint, IN
  in_green smallint, IN in_blue smallint)
  RETURNS double precision
  AS $$
BEGIN
  RETURN gwapese.y_to_lstar (gwapese.rgb_to_y (cast(in_red AS double precision)
    / 255.0, cast(in_green AS double precision) / 255.0, cast(in_blue AS double
    precision) / 255.0));
END;
$$
LANGUAGE plpgsql
IMMUTABLE;

CREATE TABLE gwapese.color_sample_reference_perception (
  blue smallint NOT NULL,
  color_id integer NOT NULL,
  green smallint NOT NULL,
  material text NOT NULL,
  perceived_lightness double precision GENERATED ALWAYS AS
    (gwapese.rgb_to_lightness (red, green, blue)) STORED NOT NULL,
  red smallint NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT color_sample_reference_perception_pk PRIMARY KEY (color_id, material),
  CONSTRAINT color_sample_reference_identifies_perception_fk FOREIGN KEY
    (color_id, material, red, green, blue) REFERENCES
    gwapese.color_sample_reference (color_id, material, red, green, blue) ON
    DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.color_sample_reference_perception_history (
  LIKE gwapese.color_sample_reference_perception
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'color_sample_reference_perception', 'color_sample_reference_perception_history');

COMMIT;
