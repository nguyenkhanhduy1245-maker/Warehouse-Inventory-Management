class ReportNode:
    def __init__(self, product):
        self.product = product
        self.next = None

class ReportLinkedList:
    def __init__(self):
        self.head = None

    def add_to_report(self, product):
        new_node = ReportNode(product)
        new_node.next = self.head
        self.head = new_node

    def display_report(self):
        current = self.head
        if not current:
            print("Không có dữ liệu báo cáo.")
            return
            
        while current:
            print(current.product)
            current = current.next

    def to_list(self):
        result = []
        current = self.head
        while current:
            result.append(current.product.to_dict())
            current = current.next
        return result

    def pop_head(self):
        if not self.head:
            return None
        node = self.head
        self.head = self.head.next
        return node.product