ALTER TABLE `suppliers` ADD `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP AFTER `updated_at`, ADD `supplier_sku` VARCHAR(255) NULL AFTER `created_at`, ADD `internal_sku` VARCHAR(255) NULL AFTER `supplier_sku`, ADD `storage_location` VARCHAR(255) NULL AFTER `internal_sku`;