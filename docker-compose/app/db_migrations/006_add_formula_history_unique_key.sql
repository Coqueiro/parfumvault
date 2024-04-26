ALTER TABLE pvault.formula_history
ADD COLUMN (fid_ingredient_hash INT(11) NOT NULL);

ALTER TABLE pvault.formula_history
ADD UNIQUE KEY fid_ingredient_hash (fid_ingredient_hash);