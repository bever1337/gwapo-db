-- Revert gawpo-db:skins from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_type',
  'historical_skin_type');

DROP TABLE gwapese.historical_skin_type;

DROP TABLE gwapese.skin_type;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin',
  'historical_skin');

DROP TABLE gwapese.historical_skin;

DROP TABLE gwapese.skin;

COMMIT;
