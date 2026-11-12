<?php
require_once __DIR__ . '/../includes/bootstrap.php';
requireLoginPage();

$error   = '';
$success = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $itemID = (int) ($_POST['itemID'] ?? 0);
    $item   = ItemRepository::getById($itemID);

    if ($itemID <= 0 || !$item) {
        $error = 'Please select a valid item.';
    } else {
        try {
            $orderID = OrderRepository::create((int) $_SESSION['userID'], [$itemID]);
            header('Location: order.php?success=' . $orderID);   // avoids double submit on refresh
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

<h2>Place an Order</h2>

<?php if ($error !== ''): ?>
    <p style="color: red;"><?= htmlspecialchars($error) ?></p>
<?php endif; ?>

<?php if ($success !== ''): ?>
    <p style="color: green;"><?= htmlspecialchars($success) ?></p>
<?php endif; ?>

<form method="POST" action="order.php">
    <label for="itemID">Select an item:</label>
    <select class="form-select" id="itemID" name="itemID" required>
        <option value="">Select an item</option>
        <?php foreach ($items as $item): ?>
            <option value="<?= (int) $item['productID'] ?>">
                Item <?= (int) $item['productID'] ?> - <?= htmlspecialchars($item['Location']) ?>
                <?php if (!empty($item['details'])): ?>
                    (<?= htmlspecialchars($item['details']) ?>)
                <?php endif; ?>
            </option>
        <?php endforeach; ?>
    </select>
    <button type="submit" name="place_order">Place Order</button>
</form>


<?php include __DIR__ . '/Classes/orders_list.php'; ?>

<?php include __DIR__ . '/Classes/footer.php'; ?>