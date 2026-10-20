<?php
class UserRepository {
    public static function findByUsername(string $uname): ?array {
        $rows = RDSdb::getDataFromSQL(
            "SELECT UserID, Uname, Password FROM Users WHERE Uname = ?", [$uname]);
        return $rows[0] ?? null;
    }

    public static function create(string $uname, string $plainPassword): int {
        return (int) RDSdb::executeSQL(
            "INSERT INTO Users (Uname, Password) VALUES (?, ?)",
            [$uname, password_hash($plainPassword, PASSWORD_DEFAULT)],
            true   // returns the new UserID
        );
    }

    public static function findById(int $userID): ?array {
    $rows = RDSdb::getDataFromSQL(
        "SELECT UserID, Uname FROM Users WHERE UserID = ?", [$userID]);
    return $rows[0] ?? null;
}
}