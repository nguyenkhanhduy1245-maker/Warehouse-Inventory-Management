class Order:
    def __init__(self, order_id, customer_name, product_id, quantity):
        self.order_id = order_id
        self.customer_name = customer_name
        self.product_id = product_id
        self.quantity = quantity
        self.status = "pending"  # Trạng thái: pending (chờ xử lý), processed (đã xử lý)

    def to_dict(self):
        return {
            "order_id": self.order_id,
            "customer_name": self.customer_name,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "status": self.status
        }
