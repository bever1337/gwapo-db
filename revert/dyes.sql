-- Revert gawpo-db:color from pg
BEGIN;

DROP FUNCTION gwapese.srgb_to_lin;

DROP FUNCTION gwapese.rgb_to_hex;

DROP FUNCTION gwapese.rgb_to_y;

DROP FUNCTION gwapese.y_to_lstar;

DROP FUNCTION gwapese.rgb_to_lightness;

DROP TABLE gwapese.historical_color_sample;

DROP TABLE gwapese.color_sample;

DROP TABLE gwapese.historical_color_name;

DROP TABLE gwapese.color_name;

DROP TABLE gwapese.historical_color;

DROP TABLE gwapese.color;

COMMIT;
