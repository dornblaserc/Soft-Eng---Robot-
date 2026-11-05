<?php
require_once __DIR__ . '/../includes/bootstrap.php';

if (isLoggedIn()) { header('Location: profile.php'); exit; }

$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $uname = trim($_POST['username'] ?? '');
    $pass  = $_POST['password'] ?? '';

    if ($uname === '' || strlen($uname) > 45) {
        $error = 'Username must be 1-45 characters.';
    } elseif (strlen($pass) < 8) {
        $error = 'Password must be at least 8 characters.';
    } elseif (UserRepository::findByUsername($uname)) {
        $error = 'That username is already taken.';
    } else {
        $id = UserRepository::create($uname, $pass);
        session_regenerate_id(true);
        $_SESSION['userID'] = $id;
        $_SESSION['uname']  = $uname;
        header('Location: profile.php');
        exit;
    }
}

$pageTitle = 'Register - Etown Robotic Delivery Systems';
include __DIR__ . '/Classes/header.php';
?>

<link rel="stylesheet" href="Styles/login.css?v=1">

<div class="auth-page">
    <div class="auth-card">
        <h2 class="auth-title">Create an account</h2>
        <p class="auth-subtitle">Register to place and track your orders.</p>

        <?php if ($error): ?>
            <div class="auth-error"><?= htmlspecialchars($error) ?></div>
        <?php endif; ?>

        <form method="post" action="register.php" class="auth-form">
            <label for="username">Username</label>
            <input type="text" id="username" name="username" maxlength="45"
                   autocomplete="username"
                   value="<?= htmlspecialchars($_POST['username'] ?? '') ?>" required autofocus>

            <label for="password">Password</label>
            <input type="password" id="password" name="password" minlength="8"
                   autocomplete="new-password" required>

            <button type="submit" class="auth-button">Register</button>
        </form>

        <p class="auth-footer">Already have an account? <a href="login.php">Log in</a></p>
    </div>
</div>

<?php include __DIR__ . '/Classes/footer.php'; ?>