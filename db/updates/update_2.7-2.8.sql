ALTER TABLE `formulasMetaData` ADD `isProtected` INT NOT NULL DEFAULT '0' AFTER `image`; 
ALTER TABLE `settings` ADD `multi_dim_perc` INT NOT NULL DEFAULT '0' AFTER `pubchem_view`; 
ALTER TABLE `settings` ADD `mUnit` VARCHAR(10) NOT NULL DEFAULT 'ml' AFTER `multi_dim_perc`; 
ALTER TABLE `ingCategory` ADD `image` LONGTEXT NULL AFTER `notes`;
ALTER TABLE `ingredients` ADD `molecularWeight` VARCHAR(255) NULL AFTER `isPrivate`;
