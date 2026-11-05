<?php
require_once __DIR__ . '/../includes/bootstrap.php';
requireLoginPage();

$error   = '';
$success = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $rawID  = $_POST['itemID'] ?? '';
    $itemID = (int) $rawID;
    $item   = ($rawID === '') ? null : ItemRepository::getById($itemID);

    if ($rawID === '' || $itemID < 0 || !$item) {
        $error = 'Please select a valid item.';
    } else {
        try {
            $orderID = OrderRepository::create((int) $_SESSION['userID'], [$itemID]);
            header('Location: order.php?success=' . $orderID);
            exit;
        } catch (Exception $e) {
            $error = 'Could not place your order. Please try again.';
        }
    }
}

if (isset($_GET['success'])) {
    $success = 'Order #' . (int) $_GET['success'] . ' placed! The robot will pick it up shortly.';
}

$items  = ItemRepository::getAll();
$orders = OrderRepository::getByUserWithItems((int) $_SESSION['userID']);
list($activeOrders, $historyOrders) = OrderRepository::splitActiveAndHistory($orders);

$pageTitle = 'Order - Etown Robotic Delivery Systems';
include __DIR__ . '/Classes/header.php';
?>

<link rel="stylesheet" href="order.css?v=1">

<div class="page">

    <h2 class="page-title">Place an Order</h2>
    <p class="page-subtitle">Choose an item and our robot will deliver it.</p>

    <?php if ($error !== ''): ?>
        <div class="alert alert-error"><?= htmlspecialchars($error) ?></div>
    <?php endif; ?>

    <?php if ($success !== ''): ?>
        <div class="alert alert-success"><?= htmlspecialchars($success) ?></div>
    <?php endif; ?>

    <section class="card">
        <form method="POST" action="order.php" class="order-form">
            <label for="itemID">Select an item</label>
            <div class="form-row">
                <select class="form-select" id="itemID" name="itemID" required>
                    <option value="">Choose an item...</option>
                    <?php foreach ($items as $item): ?>
                        <option value="<?= (int) $item['productID'] ?>">
                            <?= htmlspecialchars($item['name']) ?>
                            <?php if (!empty($item['details'])): ?>
                                (<?= htmlspecialchars($item['details']) ?>)
                            <?php endif; ?>
                        </option>
                    <?php endforeach; ?>
                </select>
                <button type="submit" name="place_order" class="btn-primary">Place Order</button>
            </div>
        </form>
    </section>

    <section class="card">
        <?php include __DIR__ . '/Classes/orders_list.php'; ?>
    </section>

</div>

<?php include __DIR__ . '/Classes/footer.php'; ?>