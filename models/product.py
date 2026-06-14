from datetime import datetime

class Product:
    def __init__(self, product_id, name, quantity, expiry_date):
        self.product_id = product_id
        self.name = name
        self.quantity = quantity
        self.expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d')

    # Phục vụ cho Priority Queue (Min-Heap sắp xếp theo ngày hết hạn)
    def __lt__(self, other):
        return self.expiry_date < other.expiry_date
    
    def __str__(self):
        return f"[{self.product_id}] {self.name} - SL: {self.quantity} - HSD: {self.expiry_date.strftime('%Y-%m-%d')}"

    def to_dict(self):
        data = {
            "product_id": self.product_id,
            "name": self.name,
            "quantity": self.quantity,
            "expiry_date": self.expiry_date.strftime('%Y-%m-%d')
        }
        if hasattr(self, 'exported_at'):
            data["exported_at"] = self.exported_at.strftime('%Y-%m-%d %H:%M:%S')
        return data