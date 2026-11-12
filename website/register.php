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

<h2>Create an Account</h2>
<?php if ($error): ?>
    <p style="color:red"><?= htmlspecialchars($error) ?></p>
<?php endif; ?>

<form method="post" action="register.php">
    <label>Username <input type="text" name="username" required></label><br>
    <label>Password <input type="password" name="password" required></label><br>
    <button type="submit">Register</button>
</form>
<p>Already have an account? <a href="login.php">Log in</a></p>

<?php include __DIR__ . '/Classes/footer.php'; ?>