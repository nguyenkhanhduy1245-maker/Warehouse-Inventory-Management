"""
Binary Search Tree for Inventory Management.
Batches are organized by expiry_date in BST (FEFO - First Expired First Out).
Each node can store multiple batches with same expiry_date.
"""
from copy import copy

class Node:
    def __init__(self, batch):
        self.batches = [batch]
        self.left = None
        self.right = None
        self.height = 1

class InventoryBST:
    def __init__(self):
        self.root = None
        self.products = {}

    def insert(self, batch):
        """Insert batch into BST sorted by expiry_date"""
        self.root = self._insert_recursive(self.root, batch)
        
        product_id = batch.product_id
        if product_id not in self.products:
            self.products[product_id] = {'name': batch.name, 'batches': [], 'total_qty': 0}
        self.products[product_id]['batches'].append(batch)
        self.products[product_id]['total_qty'] += batch.quantity

    def _insert_recursive(self, node, batch):
        if node is None:
            return Node(batch)
        
        # So sánh theo expiry_date (FEFO)
        if batch.expiry_date < node.batches[0].expiry_date:
            node.left = self._insert_recursive(node.left, batch)
        elif batch.expiry_date > node.batches[0].expiry_date:
            node.right = self._insert_recursive(node.right, batch)
        else:
            # Cùng expiry_date - thêm vào node hiện tại
            node.batches.append(batch)
        
        return node

    def search(self, product_id):
        """Search all batches by product_id using hash map for O(1) lookup"""
        if product_id not in self.products:
            return None
            
        batches = [b for b in self.products[product_id]['batches'] if b.quantity > 0]
        if not batches:
            return None

        class ProductView:
            def __init__(self, product_id, name, total_qty, batches):
                self.product_id = product_id
                self.name = name
                self.quantity = total_qty
                self.batches = batches

            def __str__(self):
                return f"[{self.product_id}] {self.name} - SL: {self.quantity}"
                
            def to_dict(self):
                return {
                    "product_id": self.product_id,
                    "name": self.name,
                    "quantity": self.quantity,
                    "batches": [b.to_dict() for b in self.batches]
                }

        total_qty = sum(b.quantity for b in batches)
        return ProductView(product_id, self.products[product_id]['name'], total_qty, batches)

    def reduce_batch_quantity(self, batch, qty):
        """Giảm số lượng batch"""
        success = self._reduce_recursive(self.root, batch, qty)
        return success

    def _reduce_recursive(self, node, batch, qty):
        if node is None:
            return False
        
        # Tìm node chứa batch
        if batch.expiry_date == node.batches[0].expiry_date:
            for b in node.batches:
                if b is batch or (b.product_id == batch.product_id and b.name == batch.name):
                    if b.quantity > qty:
                        b.quantity -= qty
                        return True
                    else:
                        b.quantity = 0
                        return True
            return False
        
        # Tìm trong left/right
        if batch.expiry_date < node.batches[0].expiry_date:
            return self._reduce_recursive(node.left, batch, qty)
        else:
            return self._reduce_recursive(node.right, batch, qty)

    def remove_batch(self, batch):
        """Xóa batch khỏi BST"""
        self.root = self._remove_recursive(self.root, batch)

    def _remove_recursive(self, node, batch):
        if node is None:
            return None
        
        if batch.expiry_date == node.batches[0].expiry_date:
            for i, b in enumerate(node.batches):
                if b is batch or (b.product_id == batch.product_id and b.expiry_date == batch.expiry_date):
                    node.batches.pop(i)
                    break
                    
            if not node.batches:
                # Node có 2 con
                if node.left and node.right:
                    min_node = self._find_min(node.right)
                    node.batches = [copy(min_node.batches[0])]
                    node.right = self._remove_recursive(node.right, min_node.batches[0])
                # Node có 1 con
                elif node.left:
                    return node.left
                elif node.right:
                    return node.right
                # Node leaf
                else:
                    return None
            return node
        
        if batch.expiry_date < node.batches[0].expiry_date:
            node.left = self._remove_recursive(node.left, batch)
        else:
            node.right = self._remove_recursive(node.right, batch)
        
        return node

    def _find_min(self, node):
        """Tìm node nhỏ nhất (leftmost)"""
        while node.left:
            node = node.left
        return node

    def get_all_products(self):
        """In-order traversal để lấy tất cả batches"""
        result = []
        self._inorder_traversal(self.root, result)
        return result

    def _inorder_traversal(self, node, result):
        """Duyệt BST theo thứ tự (expiry_date từ nhỏ đến lớn)"""
        if node is None:
            return
        
        self._inorder_traversal(node.left, result)
        result.extend(node.batches)
        self._inorder_traversal(node.right, result)