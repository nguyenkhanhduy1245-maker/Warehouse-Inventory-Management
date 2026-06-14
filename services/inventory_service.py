from datetime import datetime
from copy import copy

from models.product import Product
from models.transaction import Transaction
from data_structures.hash import InventoryBST
from data_structures.stack import TransactionStack
from data_structures.linked_list import ReportLinkedList
from data_structures.queue import OrderQueue
from models.order import Order

class InventoryService:
    def __init__(self):
        self.bst = InventoryBST()
        self.undo_stack = TransactionStack()
        self.exported_list = ReportLinkedList()
        self.order_queue = OrderQueue()

    def import_product(self, product_id, name, quantity, expiry_date):
        if quantity <= 0:
            raise ValueError("Số lượng phải lớn hơn 0")
            
        product = Product(product_id, name, quantity, expiry_date)
        
        # Thêm vào BST để tra cứu nhanh
        self.bst.insert(product)
        
        # Ghi log giao dịch vào Stack
        trans = Transaction("IMPORT", product_id, quantity)
        trans.expiry_date = product.expiry_date
        self.undo_stack.push_transaction(trans)
        return {"status": "success", "message": f"Đã nhập {quantity} {name} vào kho.", "product_id": product_id}

    def export_fefo(self):
        if self.order_queue.is_empty():
            return {"status": "error", "message": "Không có đơn hàng nào đang trong quá trình xử lí!"}

        # Lấy đơn hàng đầu tiên (FIFO)
        order = self.order_queue.dequeue()
        product_id = order.product_id
        qty_to_export = order.quantity

        entry = self.bst.products.get(product_id)
        if not entry or entry['total_qty'] < qty_to_export:
            # Hoàn lại đơn hàng vào đầu hàng đợi
            self.order_queue.queue.appendleft(order)
            return {"status": "error", "message": f"Không đủ số lượng sản phẩm {product_id} cho đơn hàng {order.order_id}!"}

        remaining_qty = qty_to_export
        batches_deducted = []
        i = 0

        # Trừ số lượng từ các lô hàng theo thứ tự (FEFO)
        while remaining_qty > 0 and i < len(entry['batches']):
            batch = entry['batches'][i]
            if batch.quantity <= remaining_qty:
                deducted = batch.quantity
                remaining_qty -= deducted
                batches_deducted.append((batch, deducted))
                entry['total_qty'] -= deducted
                entry['batches'].pop(i)
            else:
                deducted = remaining_qty
                batch.quantity -= remaining_qty
                remaining_qty = 0
                batches_deducted.append((batch, deducted))
                entry['total_qty'] -= deducted
                i += 1

        if entry['total_qty'] == 0:
            del self.bst.products[product_id]

        # Ghi nhận vào danh sách đã xuất
        now = datetime.now()
        for b, d_qty in batches_deducted:
            exported_record = copy(b)
            exported_record.quantity = d_qty
            exported_record.exported_at = now
            self.exported_list.add_to_report(exported_record)

        # Ghi log giao dịch vào Stack để Undo
        trans = Transaction("EXPORT", product_id, qty_to_export)
        trans.order_ref = order
        trans.batches_deducted = batches_deducted
        self.undo_stack.push_transaction(trans)

        return {"status": "success", "message": f"Đã xuất đơn hàng {order.order_id} (SP: {entry['name']}, SL: {qty_to_export})", "product": {"product_id": product_id, "name": entry['name'], "quantity": qty_to_export}}

    def search_product(self, product_id):
        product = self.bst.search(product_id)
        if product:
            return {"status": "success", "product": product.to_dict()}
        else:
            return {"status": "error", "message": f"Không tìm thấy sản phẩm mã {product_id}"}

    def display_all_products(self):
        # Lấy toàn bộ sản phẩm bằng thuật toán duyệt In-order của BST
        products = self.bst.get_all_products()
        # Sắp xếp theo mã sản phẩm
        products.sort(key=lambda p: p.product_id)
        return [p.to_dict() for p in products]

    def display_exported_products(self):
        # Duyệt Linked List các kiện hàng đã xuất khỏi kho (mới nhất ở đầu)
        return self.exported_list.to_list()

    def add_order(self, order_id, customer_name, product_id, quantity):
        order = Order(order_id, customer_name, product_id, quantity)
        self.order_queue.enqueue(order)
        return {"status": "success", "message": f"Đã thêm đơn hàng {order_id} của {customer_name} vào hàng đợi.", "order": order.to_dict()}

    def get_pending_orders(self):
        orders = self.order_queue.get_all_orders()
        return [o.to_dict() for o in orders]

    def get_pending_orders_count(self):
        return self.order_queue.get_size()

    def undo_last_action(self):
        # Rút giao dịch cuối cùng ra khỏi Stack
        last_trans = self.undo_stack.undo_last()
        if not last_trans:
            return {"status": "error", "message": "Ngăn xếp Undo trống, không có thao tác nào để hoàn tác!"}
            
        if last_trans.action_type == "IMPORT":
            entry = self.bst.products.get(last_trans.product_id)
            if entry:
                entry['total_qty'] -= last_trans.quantity
                
                # Tìm và xoá batch tương ứng khỏi list batches
                for i in range(len(entry['batches'])-1, -1, -1):
                    b = entry['batches'][i]
                    trans_exp = getattr(last_trans, 'expiry_date', None)
                    if b.product_id == last_trans.product_id and b.quantity == last_trans.quantity:
                        if trans_exp is None or b.expiry_date == trans_exp:
                            entry['batches'].pop(i)
                            break
                            
                if entry['total_qty'] == 0:
                    del self.bst.products[last_trans.product_id]
                    
                return {"status": "success", "message": f"Đã hủy lệnh NHẬP. Trừ {last_trans.quantity} SP mã {last_trans.product_id}"}
                
        elif last_trans.action_type == "EXPORT":
            # Hoàn tác XUẤT FEFO: 
            # 1. Khôi phục lại số lượng cho các lô hàng đã bị trừ
            entry = self.bst.products.get(last_trans.product_id)
            if not entry:
                # Nếu sản phẩm đã bị xóa khỏi BST vì hết hàng, tạo lại
                self.bst.products[last_trans.product_id] = {'name': last_trans.batches_deducted[0][0].name, 'batches': [], 'total_qty': 0}
                entry = self.bst.products[last_trans.product_id]
            
            for b, qty in reversed(last_trans.batches_deducted):
                b.quantity += qty
                entry['total_qty'] += qty
                if b not in entry['batches']:
                    entry['batches'].insert(0, b)

            # 2. Đưa đơn hàng trở lại đầu hàng đợi
            self.order_queue.queue.appendleft(last_trans.order_ref)

            # 3. Gỡ các bản ghi xuất kho tương ứng khỏi Linked List
            for _ in last_trans.batches_deducted:
                self.exported_list.pop_head()
                
            return {"status": "success", "message": f"Đã hủy lệnh XUẤT. Khôi phục đơn hàng {last_trans.order_ref.order_id}."}
        
        return {"status": "error", "message": "Lỗi hoàn tác không xác định"}