<?php
class ItemRepository {
    public static function getAll(): array {
        return RDSdb::getDataFromSQL(
            "SELECT i.productID, i.Location, i.height, i.width, i.quantity, n.details
             FROM Items i
             LEFT JOIN Instructions n ON n.instructionID = i.instructionID");
    }

    public static function getById(int $productID): ?array {
        $rows = RDSdb::getDataFromSQL(
            "SELECT * FROM Items WHERE productID = ?", [$productID]);
        return $rows[0] ?? null;
    }
}