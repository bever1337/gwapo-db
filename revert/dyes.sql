-- Revert gawpo-db:dyes from pg
BEGIN;

DROP FUNCTION gwapese.srgb_to_lin;

DROP FUNCTION gwapese.rgb_to_hex;

DROP FUNCTION gwapese.rgb_to_y;

DROP FUNCTION gwapese.y_to_lstar;

DROP FUNCTION gwapese.rgb_to_lightness;

DROP PROCEDURE gwapese.upsert_detailed_color;

DROP PROCEDURE gwapese.upsert_named_color;

DROP PROCEDURE gwapese.upsert_color;

DROP TABLE gwapese.detailed_colors;

DROP TABLE gwapese.named_colors;

DROP TABLE gwapese.colors;

DROP TABLE gwapese.color_hue_categories;

DROP TABLE gwapese.color_material_categories;

DROP TABLE gwapese.color_rarity_categories;

DROP TABLE gwapese.dyed_materials;

COMMIT;
