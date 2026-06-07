from models.product import Product
from models.transaction import Transaction
from data_structures.bst import InventoryBST
from data_structures.priority_queue import ExpiryPriorityQueue
from data_structures.stack import TransactionStack

class InventoryService:
    def __init__(self):
        self.bst = InventoryBST()
        self.pq = ExpiryPriorityQueue()
        self.undo_stack = TransactionStack()

    def import_product(self, product_id, name, quantity, expiry_date):
        product = Product(product_id, name, quantity, expiry_date)
        
        # Thêm vào BST để tra cứu nhanh
        self.bst.insert(product)
        # Thêm vào PQ để chuẩn bị xuất theo FEFO
        self.pq.push_product(product)
        
        # Ghi log giao dịch vào Stack
        self.undo_stack.push_transaction(Transaction("IMPORT", product_id, quantity))
        print(f"[THÀNH CÔNG] Đã nhập {quantity} {name} vào kho.")

    def export_fefo(self):
        if self.pq.is_empty():
            print("[LỖI] Kho hiện đang trống, không có hàng để xuất!")
            return

        # Lấy sản phẩm cận date nhất ra khỏi PQ
        product_to_export = self.pq.pop_expired_first()
        
        # Cập nhật số lượng trong BST
        bst_product = self.bst.search(product_to_export.product_id)
        if bst_product:
            exported_qty = product_to_export.quantity
            bst_product.quantity -= exported_qty
            
            # Ghi log giao dịch vào Stack để sau này có thể Undo
            trans = Transaction("EXPORT", bst_product.product_id, exported_qty)
            trans.product_ref = product_to_export # Lưu lại reference để Undo ném lại vào PQ
            self.undo_stack.push_transaction(trans)
            
            print(f"[THÀNH CÔNG] Đã xuất theo FEFO: {product_to_export.name} (HSD: {product_to_export.expiry_date.strftime('%Y-%m-%d')})")

    def search_product(self, product_id):
        product = self.bst.search(product_id)
        if product:
            print(f"Kết quả tra cứu: {product}")
        else:
            print(f"[LỖI] Không tìm thấy sản phẩm mã {product_id}")

    def display_all_products(self):
        # Lấy toàn bộ sản phẩm bằng thuật toán duyệt In-order của BST
        products = self.bst.get_all_products()
        
        if not products:
            print("[THÔNG BÁO] Kho hiện đang trống!")
            return
            
        print("\nDANH SÁCH TOÀN BỘ SẢN PHẨM TRONG KHO (Sắp xếp theo Mã SP):")
        print("-" * 65)
        for p in products:
            print(p)
        print("-" * 65)
        print(f"Tổng cộng: {len(products)} mặt hàng.")

    def undo_last_action(self):
        # Rút giao dịch cuối cùng ra khỏi Stack
        last_trans = self.undo_stack.undo_last()
        if not last_trans:
            print("[THÔNG BÁO] Ngăn xếp Undo trống, không có thao tác nào để hoàn tác!")
            return
            
        if last_trans.action_type == "IMPORT":
            # Hoàn tác NHẬP: Trừ số lượng trong BST
            product = self.bst.search(last_trans.product_id)
            if product:
                product.quantity -= last_trans.quantity
                print(f"[HOÀN TÁC] Đã hủy lệnh NHẬP. Trừ {last_trans.quantity} SP mã {last_trans.product_id}")
                
        elif last_trans.action_type == "EXPORT":
            # Hoàn tác XUẤT: (Đúng chuẩn logic trong Audit Log)
            # 1. Cộng lại số lượng vào BST
            product = self.bst.search(last_trans.product_id)
            if product:
                product.quantity += last_trans.quantity
                
            # 2. Push sản phẩm trở lại Priority Queue để không làm hỏng quy tắc FEFO
            if hasattr(last_trans, 'product_ref'):
                self.pq.push_product(last_trans.product_ref)
                
            print(f"[HOÀN TÁC] Đã hủy lệnh XUẤT. Khôi phục SP mã {last_trans.product_id} vào kho và hàng đợi.")