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