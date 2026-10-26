<?php
class OrderRepository {

    // Creates the order and its item rows together, or neither
    public static function create($userID, array $productIDs) {
        RDSdb::startTransaction();
        try {
            $orderID = (int) RDSdb::executeSQL(
                "INSERT INTO `Order` (status, userID) VALUES ('Pending', ?)",
                [$userID],
                true   // return the new orderID
            );

            foreach ($productIDs as $productID) {
                RDSdb::executeSQL(
                    "INSERT INTO `Item Orders` (productID, orderID) VALUES (?, ?)",
                    [$productID, $orderID]
                );
            }

            RDSdb::commitTransaction();
            return $orderID;
        } catch (Exception $e) {
            RDSdb::rollbackTransaction();
            throw $e;
        }
    }

    public static function getByUser($userID) {
        return RDSdb::getDataFromSQL(
            "SELECT orderID, status FROM `Order` WHERE userID = ? ORDER BY orderID DESC",
            [$userID]
        );
    }


    // All of a user's orders with their items, newest first
public static function getByUserWithItems($userID) {
    $rows = RDSdb::getDataFromSQL(
        "SELECT o.orderID, o.status, i.productID, i.Location
         FROM `Order` o
         LEFT JOIN `Item Orders` io ON io.orderID = o.orderID
         LEFT JOIN Items i ON i.productID = io.productID
         WHERE o.userID = ?
         ORDER BY o.orderID DESC, i.productID",
        [$userID]
    );

    // The join returns one row per item, so group the rows by order
    $orders = [];
    foreach ($rows as $row) {
        $id = $row['orderID'];
        if (!isset($orders[$id])) {
            $orders[$id] = [
                'orderID' => $id,
                'status'  => $row['status'],
                'items'   => []
            ];
        }
        if ($row['productID'] !== null) {
            $orders[$id]['items'][] = [
                'productID' => $row['productID'],
                'Location'  => $row['Location']
            ];
        }
    }
    return array_values($orders);
}


// Splits a list of orders into [active, history] by status
public static function splitActiveAndHistory(array $orders) {
    $activeStatuses = ['Pending', 'Claimed', 'InProgress'];
    $active  = [];
    $history = [];
    foreach ($orders as $o) {
        if (in_array($o['status'], $activeStatuses, true)) {
            $active[] = $o;
        } else {
            $history[] = $o;
        }
    }
    return [$active, $history];
}
}