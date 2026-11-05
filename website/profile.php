<?php
require_once __DIR__ . '/../includes/bootstrap.php';
requireLoginPage();

$user   = UserRepository::findById((int) $_SESSION['userID']);
$orders = OrderRepository::getByUserWithItems((int) $_SESSION['userID']);
list($activeOrders, $historyOrders) = OrderRepository::splitActiveAndHistory($orders);

$pageTitle = 'Profile - Etown Robotic Delivery Systems';
include __DIR__ . '/Classes/header.php';
?>

<link rel="stylesheet" href="Styles/order.css?v=1">
<link rel="stylesheet" href="Styles/profile.css?v=1">

<div class="page">

    <h2 class="page-title">My Profile</h2>
    <p class="page-subtitle">Your account details and order activity.</p>

    <?php if ($user): ?>

        <section class="card">
            <div class="profile-banner">
                <div class="profile-avatar">
                    <?= htmlspecialchars(mb_strtoupper(mb_substr($user['Uname'], 0, 1))) ?>
                </div>
                <div class="profile-info">
                    <h2><?= htmlspecialchars($user['Uname']) ?></h2>
                    <p class="profile-meta">User ID: <?= htmlspecialchars($user['UserID']) ?></p>
                </div>
                <a href="order.php" class="btn-primary">Place a new order</a>
            </div>
        </section>

        <div class="stats">
            <div class="stat">
                <div class="stat-number"><?= count($orders) ?></div>
                <div class="stat-label">Total orders</div>
            </div>
            <div class="stat">
                <div class="stat-number"><?= count($activeOrders) ?></div>
                <div class="stat-label">Active</div>
            </div>
            <div class="stat">
                <div class="stat-number"><?= count($historyOrders) ?></div>
                <div class="stat-label">Completed</div>
            </div>
        </div>

    <?php else: ?>
        <div class="alert alert-error">User not found.</div>
    <?php endif; ?>

    <section class="card">
        <?php include __DIR__ . '/Classes/orders_list.php'; ?>
    </section>

</div>

<?php include __DIR__ . '/Classes/footer.php'; ?>