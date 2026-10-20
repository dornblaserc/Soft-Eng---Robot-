<?php

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
require_once __DIR__ . '/../includes/config.php';
require_once __DIR__ . '/../includes/RDSdb.php';
require_once __DIR__ . '/../includes/repos/UserRepo.php';


session_start();

// TEMPORARY until login exists: pretend user 1 is logged in
$_SESSION['userID'] = $_SESSION['userID'] ?? 1;

$user = UserRepository::findById((int) $_SESSION['userID']);


$pageTitle = 'Profile - Etown Robotic Delivery Systems';
include 'Classes/header.php';
?>

<h2>My Profile</h2>

<?php if ($user): ?>
    <p>Welcome, <strong><?= htmlspecialchars($user['Uname']) ?></strong></p>
    <p>User ID: <?= htmlspecialchars($user['UserID']) ?></p>
<?php else: ?>
    <p>User not found.</p>
<?php endif; ?>

<?php include 'Classes/footer.php'; ?>