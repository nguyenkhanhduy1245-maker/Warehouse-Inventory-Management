from datetime import datetime
from data_structures.linked_list import ReportLinkedList

class ReportService:
    def __init__(self, inventory_service):
        self.inventory_service = inventory_service

    def generate_expiry_report(self, days_threshold=30):
        report_list = ReportLinkedList()
        all_products = self.inventory_service.bst.get_all_products()
        
        now = datetime.now()
        for product in all_products:
            # Tính số ngày còn lại
            days_left = (product.expiry_date - now).days
            if days_left <= days_threshold:
                report_list.add_to_report(product)
                
        return report_list.to_list()