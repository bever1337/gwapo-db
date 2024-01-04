-- Revert gawpo-db:color from pg
BEGIN;

DROP FUNCTION gwapese.srgb_to_lin;

DROP FUNCTION gwapese.rgb_to_hex;

DROP FUNCTION gwapese.rgb_to_y;

DROP FUNCTION gwapese.y_to_lstar;

DROP FUNCTION gwapese.rgb_to_lightness;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'color_name',
  'historical_color_name');

DROP TABLE gwapese.historical_color_name;

DROP TABLE gwapese.color_name;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'color_sample_base',
  'historical_color_sample_base');

DROP TABLE gwapese.historical_color_sample_base;

DROP TABLE gwapese.color_sample_base;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'color_sample_adjustment',
  'historical_color_sample_adjustment');

DROP TABLE gwapese.historical_color_sample_adjustment;

DROP TABLE gwapese.color_sample_adjustment;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'color_sample_shift',
  'historical_color_sample_shift');

DROP TABLE gwapese.historical_color_sample_shift;

DROP TABLE gwapese.color_sample_shift;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'color_sample_reference_perception',
  'historical_color_sample_reference_perception');

DROP TABLE gwapese.historical_color_sample_reference_perception;

DROP TABLE gwapese.color_sample_reference_perception;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'color_sample_reference',
  'historical_color_sample_reference');

DROP TABLE gwapese.historical_color_sample_reference;

DROP TABLE gwapese.color_sample_reference;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'color_sample',
  'historical_color_sample');

DROP TABLE gwapese.historical_color_sample;

DROP TABLE gwapese.color_sample;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'color',
  'historical_color');

DROP TABLE gwapese.historical_color;

DROP TABLE gwapese.color;

COMMIT;
