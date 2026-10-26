<?php
// 1. Config must load before RDSdb, because RDSdb reads its variables
require_once __DIR__ . '/config.php';
require_once __DIR__ . '/RDSdb.php';

// 2. Load the repositories
require_once __DIR__ . '/repositories/UserRepo.php';
require_once __DIR__ . '/repositories/ItemRepo.php';
require_once __DIR__ . '/repositories/OrderRepo.php';

// 3. Sessions for website logins
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

function isLoggedIn() {
    return isset($_SESSION['userID']);
}

// Put at the top of any page that needs a logged-in user
function requireLoginPage() {
    if (!isLoggedIn()) {
        header('Location: login.php');
        exit;
    }
}

// 4. Helper for API endpoints
function requireRobotKey(): void {
    global $robotApiKey;
    $sent = $_SERVER['HTTP_X_API_KEY'] ?? '';
    $expected = isset($robotApiKey) ? (string) $robotApiKey : '';
    if ($expected === '' || !hash_equals($expected, $sent)) {
        http_response_code(401);
        header('Content-Type: application/json');
        exit;
    }
}