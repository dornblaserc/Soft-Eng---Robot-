<?php
require_once __DIR__ . '/../includes/bootstrap.php';
requireLoginPage();

$user = UserRepository::findById((int) $_SESSION['userID']);

$pageTitle = 'Profile - Etown Robotic Delivery Systems';
include __DIR__ . '/Classes/header.php';
?>

<h2>My Profile</h2>

<?php if ($user): ?>
    <p>Welcome, <strong><?= htmlspecialchars($user['Uname']) ?></strong></p>
    <p>User ID: <?= htmlspecialchars($user['UserID']) ?></p>
<?php else: ?>
    <p>User not found.</p>
<?php endif; ?>

<?php include __DIR__ . '/Classes/footer.php'; ?>