"""
Reworked Inventory index: use a dict keyed by product_id and track batches per product.
This preserves a simple API used by services while supporting FEFO batches.
"""

class InventoryBST:
    def __init__(self):
        # product_id -> {'name': str, 'batches': [Batch,...], 'total_qty': int}
        self.products = {}

    def insert(self, batch):
        entry = self.products.get(batch.product_id)
        if not entry:
            self.products[batch.product_id] = {'name': batch.name, 'batches': [batch], 'total_qty': batch.quantity}
        else:
            entry['batches'].append(batch)
            entry['total_qty'] += batch.quantity

    def search(self, product_id):
        entry = self.products.get(product_id)
        if not entry:
            return None

        class ProductView:
            def __init__(self, product_id, name, total_qty):
                self.product_id = product_id
                self.name = name
                self.quantity = total_qty

            def __str__(self):
                return f"[{self.product_id}] {self.name} - SL: {self.quantity}"

        return ProductView(product_id, entry['name'], entry['total_qty'])

    def reduce_batch_quantity(self, batch, qty):
        entry = self.products.get(batch.product_id)
        if not entry:
            return

        # try to find same batch object first
        for b in entry['batches']:
            if b is batch or (b.expiry_date == batch.expiry_date and b.name == batch.name):
                if b.quantity > qty:
                    b.quantity -= qty
                    entry['total_qty'] -= qty
                else:
                    entry['total_qty'] -= b.quantity
                    entry['batches'].remove(b)
                break

        if entry['total_qty'] <= 0:
            del self.products[batch.product_id]

    def remove_batch(self, batch):
        entry = self.products.get(batch.product_id)
        if not entry:
            return
        for i, b in enumerate(entry['batches']):
            if b is batch or (b.expiry_date == batch.expiry_date and b.quantity == batch.quantity):
                entry['total_qty'] -= b.quantity
                del entry['batches'][i]
                break
        if entry['total_qty'] <= 0:
            del self.products[batch.product_id]

    def get_all_products(self):
        # return flattened list of all batches for reporting
        result = []
        for entry in self.products.values():
            result.extend(entry['batches'])
        return result