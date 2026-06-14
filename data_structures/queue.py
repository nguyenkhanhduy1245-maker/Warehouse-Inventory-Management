from collections import deque

class OrderQueue:
    def __init__(self):
        # Sử dụng deque để tối ưu việc thêm/xóa phần tử ở cả 2 đầu (O(1))
        self.queue = deque()

    def enqueue(self, order):
        """Thêm đơn hàng vào cuối hàng đợi (Vào sau)"""
        self.queue.append(order)

    def dequeue(self):
        """Lấy đơn hàng ở đầu hàng đợi ra (Ra trước)"""
        if self.is_empty():
            return None
        return self.queue.popleft()

    def is_empty(self):
        return len(self.queue) == 0

    def get_all_orders(self):
        """Trả về toàn bộ danh sách đơn hàng (chỉ để hiển thị)"""
        return list(self.queue)
