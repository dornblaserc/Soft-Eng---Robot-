<?php
require_once __DIR__ . '/../includes/bootstrap.php';
requireLoginPage();

$user   = UserRepository::findById((int) $_SESSION['userID']);
$orders = OrderRepository::getByUserWithItems((int) $_SESSION['userID']);
list($activeOrders, $historyOrders) = OrderRepository::splitActiveAndHistory($orders);

$pageTitle = 'Profile - Etown Robotic Delivery Systems';
include __DIR__ . '/Classes/header.php';
?>

<h2>My Profile</h2>

<?php if ($user): ?>
    <p>Welcome, <strong><?= htmlspecialchars($user['Uname']) ?></strong></p>
    <p>User ID: <?= htmlspecialchars($user['UserID']) ?></p>
    <p>Total orders: <?= count($orders) ?></p>
    <p><a href="order.php">Place a new order</a></p>
<?php else: ?>
    <p>User not found.</p>
<?php endif; ?>

<?php include __DIR__ . '/Classes/orders_list.php'; ?>

<?php include __DIR__ . '/Classes/footer.php'; ?>