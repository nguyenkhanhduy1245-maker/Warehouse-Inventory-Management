import heapq

class ExpiryPriorityQueue:
    def __init__(self):
        self.heap = []

    def push_product(self, product):
        heapq.heappush(self.heap, product)

    def pop_expired_first(self):
        if self.heap:
            return heapq.heappop(self.heap)
        return None
    
    def is_empty(self):
        return len(self.heap) == 0