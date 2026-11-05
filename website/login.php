<?php
require_once __DIR__ . '/../includes/bootstrap.php';

if (isLoggedIn()) { header('Location: profile.php'); exit; }

$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $uname = trim($_POST['username'] ?? '');
    $pass  = $_POST['password'] ?? '';

    $user = UserRepository::findByUsername($uname);

    if ($user && password_verify($pass, $user['Password'])) {
        session_regenerate_id(true);          // prevents session fixation
        $_SESSION['userID'] = (int) $user['UserID'];
        $_SESSION['uname']  = $user['Uname'];
        header('Location: profile.php');
        exit;
    }
    // Same message whether the user or the password was wrong, on purpose
    $error = 'Invalid username or password.';
}

$pageTitle = 'Login - Etown Robotic Delivery Systems';
include __DIR__ . '/Classes/header.php';
?>

<link rel="stylesheet" href="Styles/login.css?v=1">

<div class="auth-page">
    <div class="auth-card">
        <h2 class="auth-title">Welcome back</h2>
        <p class="auth-subtitle">Log in to place and track your orders.</p>

        <?php if ($error): ?>
            <div class="auth-error"><?= htmlspecialchars($error) ?></div>
        <?php endif; ?>

        <form method="post" action="login.php" class="auth-form">
            <label for="username">Username</label>
            <input type="text" id="username" name="username" autocomplete="username"
                   value="<?= htmlspecialchars($_POST['username'] ?? '') ?>" required autofocus>

            <label for="password">Password</label>
            <input type="password" id="password" name="password" autocomplete="current-password" required>

            <button type="submit" class="auth-button">Log in</button>
        </form>

        <p class="auth-footer">No account yet? <a href="register.php">Register</a></p>
    </div>
</div>

<?php include __DIR__ . '/Classes/footer.php'; ?>