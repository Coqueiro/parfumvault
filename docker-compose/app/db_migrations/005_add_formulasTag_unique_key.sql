ALTER TABLE pvault.formulasTags
ADD COLUMN (tag_hash INT(11) NOT NULL);

ALTER TABLE pvault.formulasTags
ADD UNIQUE KEY tag_hash (tag_hash);