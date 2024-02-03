MERGE INTO gwapese.item_upgrade AS target_item_upgrade
USING (
  SELECT
    DISTINCT
      from_item_id, to_item_id, upgrade
    FROM
      tempo_item_upgrade
    WHERE
      EXISTS (
        SELECT
          1
        FROM
          gwapese.item
        WHERE
          gwapese.item.item_id = tempo_item_upgrade.from_item_id)
          AND EXISTS (
            SELECT
              1
            FROM
              gwapese.item
            WHERE
	      gwapese.item.item_id = tempo_item_upgrade.to_item_id)) AS
		source_item_upgrade ON target_item_upgrade.from_item_id =
		source_item_upgrade.from_item_id
            AND target_item_upgrade.to_item_id = source_item_upgrade.to_item_id
            AND target_item_upgrade.upgrade = source_item_upgrade.upgrade
WHEN NOT MATCHED THEN
    INSERT
      (from_item_id, to_item_id, upgrade)
      VALUES (source_item_upgrade.from_item_id, source_item_upgrade.to_item_id,
	source_item_upgrade.upgrade);
