-- Revert gwapo-db:color from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'color_base');

DROP TABLE gwapese.color_base_history;

DROP TABLE gwapese.color_base;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'color_sample_adjustment');

DROP TABLE gwapese.color_sample_adjustment_history;

DROP TABLE gwapese.color_sample_adjustment;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'color_sample_shift');

DROP TABLE gwapese.color_sample_shift_history;

DROP TABLE gwapese.color_sample_shift;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'color_sample_reference_perception');

DROP TABLE gwapese.color_sample_reference_perception_history;

DROP TABLE gwapese.color_sample_reference_perception;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'color_sample_reference');

DROP TABLE gwapese.color_sample_reference_history;

DROP TABLE gwapese.color_sample_reference;

DROP FUNCTION gwapese.srgb_to_lin;

DROP FUNCTION gwapese.rgb_to_hex;

DROP FUNCTION gwapese.rgb_to_y;

DROP FUNCTION gwapese.y_to_lstar;

DROP FUNCTION gwapese.rgb_to_lightness;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'color_sample');

DROP TABLE gwapese.color_sample_history;

DROP TABLE gwapese.color_sample;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'color');

DROP TABLE gwapese.color_history;

DROP TABLE gwapese.color;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'color_hue');

DROP TABLE gwapese.color_hue_history;

DROP TABLE gwapese.color_hue;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'color_material');

DROP TABLE gwapese.color_material_history;

DROP TABLE gwapese.color_material;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'color_rarity');

DROP TABLE gwapese.color_rarity_history;

DROP TABLE gwapese.color_rarity;

COMMIT;
