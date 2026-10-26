<?php
// api/robot/index.php
//
// Robot API (single robot). Every route requires the X-API-Key header.
//
//   GET  /api/robot/?action=next-order
//        Returns the order the robot should work on, or {"order": null}.
//        If an order is already InProgress (robot restarted mid-delivery) that
//        same order is returned again. Otherwise the oldest Pending order is
//        marked InProgress and returned.
//
//   POST /api/robot/?action=update-status
//        Body: {"orderID": 4, "status": "Delivered"}   (or "Failed")
//        Only an InProgress order can be finished.

require_once __DIR__ . '/../../includes/bootstrap.php';

if (!function_exists('jsonResponse')) {
    function jsonResponse($data, $status = 200) {
        http_response_code($status);
        header('Content-Type: application/json');
        echo json_encode($data);
        exit;
    }
}

// One check at the top: no robot route can be added without the key
requireRobotKey();

$action = isset($_GET['action']) ? $_GET['action'] : '';
$method = $_SERVER['REQUEST_METHOD'];
$input  = json_decode(file_get_contents('php://input'), true);
if (!is_array($input)) {
    $input = [];
}

$routes = [
    'GET next-order'     => 'handleNextOrder',
    'POST update-status' => 'handleUpdateStatus',
];

$key = $method . ' ' . $action;
if (!isset($routes[$key])) {
    jsonResponse(['error' => 'Not found'], 404);
}

try {
    call_user_func($routes[$key], $input);
} catch (Exception $e) {
    // Log the real reason on the server, send a generic message to the caller
    error_log('Robot API error: ' . $e->getMessage());
    jsonResponse(['error' => 'Server error'], 500);
}

// ---------- handlers ----------

function handleNextOrder($in) {
    // 1. Is the robot already working on something? (covers a crash or restart)
    $order = OrderRepository::getFirstByStatus('InProgress');

    // 2. If not, take the oldest Pending order and mark it InProgress
    if (!$order) {
        $order = OrderRepository::getFirstByStatus('Pending');
        if ($order) {
            OrderRepository::setStatus((int) $order['orderID'], 'InProgress');
            $order['status'] = 'InProgress';
        }
    }

    if (!$order) {
        jsonResponse(['order' => null]);
    }

    jsonResponse([
        'order' => [
            'orderID' => (int) $order['orderID'],
            'status'  => $order['status'],
            'items'   => OrderRepository::getItems((int) $order['orderID']),
        ]
    ]);
}

function handleUpdateStatus($in) {
    $orderID = isset($in['orderID']) ? (int) $in['orderID'] : 0;
    $status  = isset($in['status']) ? $in['status'] : '';

    // The robot may only finish an order, not set arbitrary statuses
    $allowed = ['Delivered', 'Failed'];
    if ($orderID <= 0 || !in_array($status, $allowed, true)) {
        jsonResponse(['error' => 'orderID and a status of Delivered or Failed are required'], 400);
    }

    $order = OrderRepository::getById($orderID);
    if (!$order) {
        jsonResponse(['error' => 'Order not found'], 404);
    }
    if ($order['status'] !== 'InProgress') {
        jsonResponse(['error' => 'Order is ' . $order['status'] . ', not InProgress'], 409);
    }

    OrderRepository::setStatus($orderID, $status);
    jsonResponse(['ok' => true, 'orderID' => $orderID, 'status' => $status]);
}