ALTER TABLE pvault.formulas
ADD COLUMN (fid_ingredient_hash INT(11) NOT NULL);

ALTER TABLE pvault.formulas
ADD UNIQUE KEY fid_ingredient_hash (fid_ingredient_hash);
