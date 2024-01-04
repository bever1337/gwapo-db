-- Revert gawpo-db:race from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'race',
  'historical_race');

DROP TABLE gwapese.historical_race;

DROP TABLE gwapese.race;

COMMIT;
