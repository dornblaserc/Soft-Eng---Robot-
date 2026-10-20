<?php
class OrderRepository {
    public static function getByUser(int $userID): array {
        return RDSdb::getDataFromSQL(
            "SELECT orderID, status FROM `Order` WHERE userID = ?", [$userID]);
    }

    public static function getItems(int $orderID): array {
        return RDSdb::getDataFromSQL(
            "SELECT i.* FROM `Item Orders` io
             JOIN Items i ON i.productID = io.productID
             WHERE io.orderID = ?", [$orderID]);
    }

    public static function create(int $userID, array $productIDs): int {
        RDSdb::startTransaction();
        try {
            $orderID = (int) RDSdb::executeSQL(
                "INSERT INTO `Order` (status, userID) VALUES ('Pending', ?)",
                [$userID], true);
            foreach ($productIDs as $pid) {
                RDSdb::executeSQL(
                    "INSERT INTO `Item Orders` (productID, orderID) VALUES (?, ?)",
                    [$pid, $orderID]);
            }
            RDSdb::commitTransaction();
            return $orderID;
        } catch (Exception $e) {
            RDSdb::rollbackTransaction();
            throw $e;
        }
    }
}