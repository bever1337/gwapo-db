-- Deploy gawpo-db:dyes to pg
BEGIN;

CREATE TABLE gwapese.color_hue_categories (
  hue text NOT NULL,
  CONSTRAINT color_hue_categories_PK PRIMARY KEY (hue)
);

INSERT INTO gwapese.color_hue_categories (hue)
  VALUES ('Gray'),
  ('Brown'),
  ('Red'),
  ('Orange'),
  ('Yellow'),
  ('Green'),
  ('Blue'),
  ('Purple');

CREATE TABLE gwapese.color_material_categories (
  material text NOT NULL,
  CONSTRAINT color_material_categories_PK PRIMARY KEY (material)
);

INSERT INTO gwapese.color_material_categories (material)
  VALUES ('Vibrant'),
  ('Leather'),
  ('Metal');

CREATE TABLE gwapese.color_rarity_categories (
  rarity text NOT NULL,
  CONSTRAINT color_rarity_categories_PK PRIMARY KEY (rarity)
);

INSERT INTO gwapese.color_rarity_categories (rarity)
  VALUES ('Starter'),
  ('Common'),
  ('Uncommon'),
  ('Rare'),
  ('Exclusive');

CREATE TABLE gwapese.dyed_materials (
  material text NOT NULL,
  CONSTRAINT dyed_materials_PK PRIMARY KEY (material)
);

INSERT INTO gwapese.dyed_materials (material)
  VALUES ('cloth'),
  ('fur'),
  ('leather'),
  ('metal');

CREATE TABLE gwapese.colors (
  id smallint NOT NULL,
  hue text,
  material text,
  rarity text,
  CONSTRAINT colors_PK PRIMARY KEY (id),
  CONSTRAINT colors_FK_hue FOREIGN KEY (hue) REFERENCES
    gwapese.color_hue_categories (hue),
  CONSTRAINT colors_FK_material FOREIGN KEY (material) REFERENCES
    gwapese.color_material_categories (material),
  CONSTRAINT colors_FK_rarity FOREIGN KEY (rarity) REFERENCES
    gwapese.color_rarity_categories (rarity)
);

CREATE TABLE gwapese.detailed_colors (
  id smallint NOT NULL,
  blue smallint NOT NULL,
  brightness smallint NOT NULL,
  contrast double precision NOT NULL,
  green smallint NOT NULL,
  hue smallint NOT NULL,
  lightness double precision NOT NULL,
  material text NOT NULL,
  perceived_lightness double precision NOT NULL,
  red smallint NOT NULL,
  rgb varchar(6) NOT NULL,
  saturation double precision NOT NULL,
  CONSTRAINT detailed_colors_PK PRIMARY KEY (id, material),
  CONSTRAINT detailed_colors_CK_blue_range CHECK (blue >= 0 AND blue <= 255),
  CONSTRAINT detailed_colors_CK_green_range CHECK (green >= 0 AND green <= 255),
  CONSTRAINT detailed_colors_CK_red_range CHECK (red >= 0 AND red <= 255),
  CONSTRAINT detailed_colors_FK_id FOREIGN KEY (id) REFERENCES gwapese.colors
    (id) ON DELETE CASCADE,
  CONSTRAINT detailed_colors_FK_material FOREIGN KEY (material) REFERENCES
    gwapese.dyed_materials (material)
);

CREATE TABLE gwapese.named_colors (
  id smallint NOT NULL,
  color_name text NOT NULL,
  language_tag text NOT NULL,
  CONSTRAINT named_colors_PK PRIMARY KEY (id, language_tag),
  CONSTRAINT named_colors_FK_id FOREIGN KEY (id) REFERENCES gwapese.colors (id)
    ON DELETE CASCADE,
  CONSTRAINT named_colors_FK_language_tag FOREIGN KEY (language_tag) REFERENCES
    gwapese.language_tags (language_tag)
);

CREATE OR REPLACE PROCEDURE gwapese.upsert_color (in_id smallint, in_hue text,
  in_material text, in_rarity text)
  AS $$
BEGIN
  MERGE INTO gwapese.colors AS target_color
  USING (
  VALUES (in_id)) AS source_color (id) ON target_color.id = source_color.id
  WHEN MATCHED THEN
    UPDATE SET
      (hue, material, rarity) = (in_hue, in_material, in_rarity)
  WHEN NOT MATCHED THEN
    INSERT (id, hue, material, rarity)
      VALUES (in_id, in_hue, in_material, in_rarity);
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE gwapese.upsert_detailed_color (in_id smallint,
  in_blue smallint, in_brightness smallint, in_contrast double precision,
  in_green smallint, in_hue smallint, in_lightness double precision,
  in_material text, in_red smallint, in_saturation double precision)
  AS $$
BEGIN
  MERGE INTO gwapese.detailed_colors AS target_detailed_color
  USING (
  VALUES (in_id, in_material)) AS source_detailed_color (id, material) ON
    target_detailed_color.id = source_detailed_color.id
    AND target_detailed_color.material = source_detailed_color.material
  WHEN MATCHED THEN
    UPDATE SET
      (blue, brightness, contrast, green, hue, lightness, perceived_lightness,
	red, rgb, saturation) = (in_blue, in_brightness, in_contrast, in_green,
	in_hue, in_lightness, gwapese.rgb_to_lightness (in_red, in_green,
	in_blue), in_red, gwapese.rgb_to_hex (in_red, in_green, in_blue),
	in_saturation)
  WHEN NOT MATCHED THEN
    INSERT (id, blue, brightness, contrast, green, hue, lightness, material,
      perceived_lightness, red, rgb, saturation)
      VALUES (in_id, in_blue, in_brightness, in_contrast, in_green, in_hue,
	in_lightness, in_material, gwapese.rgb_to_lightness (in_red, in_green,
	in_blue), in_red, gwapese.rgb_to_hex (in_red, in_green, in_blue),
	in_saturation);
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE gwapese.upsert_named_color (in_id smallint,
  in_color_name text, in_language_tag text)
  AS $$
BEGIN
  MERGE INTO gwapese.named_colors AS target_named_color
  USING (
  VALUES (in_id, in_language_tag)) AS source_named_color (id, language_tag) ON
    target_named_color.id = source_named_color.id
    AND target_named_color.language_tag = source_named_color.language_tag
  WHEN MATCHED THEN
    UPDATE SET
      color_name = in_color_name
  WHEN NOT MATCHED THEN
    INSERT (id, color_name, language_tag)
      VALUES (in_id, in_color_name, in_language_tag);
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION gwapese.rgb_to_hex (IN in_red smallint, IN in_green
  smallint, IN in_blue smallint)
  RETURNS varchar (
    6
)
    AS $$
BEGIN
  RETURN LPAD(LPAD(TO_HEX(CAST(in_red AS int)), 2, '0') ||
    LPAD(TO_HEX(CAST(in_green AS int)), 2, '0') ||
    LPAD(TO_HEX(CAST(in_blue AS int)), 2, '0'), 6,
    '0');
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION gwapese.srgb_to_lin (IN in_color_channel double precision)
  RETURNS double precision
  AS $$
BEGIN
  CASE WHEN in_color_channel <= 0.04045 THEN
    RETURN in_color_channel / 12.92;
  ELSE
    RETURN POWER((in_color_channel + 0.055) / 1.055, 2.4);
  END CASE;
END;
$$
LANGUAGE plpgsql;

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
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION gwapese.y_to_lstar (IN in_y double precision)
  RETURNS double precision
  AS $$
BEGIN
  CASE WHEN in_y <= (216.0 / 24389.0) THEN
    RETURN in_y * (24389.0 / 27.0);
  ELSE
    RETURN POWER(in_y, (1.0 / 3.0)) * 116 - 16;
  END CASE;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION gwapese.rgb_to_lightness (IN in_red smallint, IN
  in_green smallint, IN in_blue smallint)
  RETURNS double precision
  AS $$
BEGIN
  RETURN gwapese.y_to_lstar (gwapese.rgb_to_y (CAST(in_red AS double precision)
    / 255.0, CAST(in_green AS double precision) / 255.0, CAST(in_blue AS double
    precision) / 255.0));
END;
$$
LANGUAGE plpgsql;

COMMIT;
