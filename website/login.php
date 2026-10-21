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

<h2>Login</h2>
<?php if ($error): ?>
    <p style="color:red"><?= htmlspecialchars($error) ?></p>
<?php endif; ?>

<form method="post" action="login.php">
    <label>Username <input type="text" name="username" required></label><br>
    <label>Password <input type="password" name="password" required></label><br>
    <button type="submit">Log in</button>
</form>
<p>No account yet? <a href="register.php">Register</a></p>

<?php include __DIR__ . '/Classes/footer.php'; ?>