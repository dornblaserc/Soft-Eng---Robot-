<?php
// Expects $activeOrders and $historyOrders to be set by the page that includes this.

if (!function_exists('renderOrdersTable')) {
    function renderOrdersTable(array $orders) { ?>
        <table>
            <tr><th>Order</th><th>Items</th><th>Status</th></tr>
            <?php foreach ($orders as $o): ?>
                <tr>
                    <td>#<?= (int) $o['orderID'] ?></td>
                    <td>
                        <?php foreach ($o['items'] as $it): ?>
                            Item <?= (int) $it['productID'] ?><br>
                        <?php endforeach; ?>
                    </td>
                    <td><?= htmlspecialchars($o['status']) ?></td>
                </tr>
            <?php endforeach; ?>
        </table>
    <?php }
}
?>

<h2>Current Orders</h2>
<?php if (count($activeOrders) === 0): ?>
    <p>You have no orders in progress.</p>
<?php else: ?>
    <?php renderOrdersTable($activeOrders); ?>
<?php endif; ?>

<h2>Order History</h2>
<?php if (count($historyOrders) === 0): ?>
    <p>No completed orders yet.</p>
<?php else: ?>
    <?php renderOrdersTable($historyOrders); ?>
<?php endif; ?>