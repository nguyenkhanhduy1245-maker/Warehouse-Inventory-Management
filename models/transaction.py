from datetime import datetime

class Transaction:
    def __init__(self, action_type, product_id, quantity):
        self.action_type = action_type  # 'IMPORT' hoặc 'EXPORT'
        self.product_id = product_id
        self.quantity = quantity
        self.timestamp = datetime.now()

    def __str__(self):
        return f"{self.action_type} | {self.product_id} | SL: {self.quantity} | {self.timestamp.strftime('%H:%M:%S')}"