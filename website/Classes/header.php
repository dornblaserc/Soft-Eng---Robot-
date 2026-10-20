<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="styles.css">
    <script src="robot.js"></script>
    <title><?= htmlspecialchars($pageTitle ?? 'Etown Robotic Delivery Systems') ?></title>
</head>

<body>

    <header class="navebar-header">
        <nav class="navbar">

            <!-- Logo Section -->
            <a href="index.php" class="logo">
                <img src="logo.png" alt="MyBrand logo" height="40">
                <span class="logo-text">Etown Robotic Delivery Systems</span>
            </a>

            <!-- Navigation Buttons -->
            <ul class="nav-menu" id="nav-menu">
                <li class="nav-item">
                    <a href="about.php" class="nav-link">About</a>
                </li>
                <li class="nav-item">
                    <a href="order.php" class="nav-link">Order</a>
                </li>
                <li class="nav-item">
                    <a href="profile.php" class="nav-link profile-btn">Profile</a>
                </li>
            </ul>

        </nav>
    </header>