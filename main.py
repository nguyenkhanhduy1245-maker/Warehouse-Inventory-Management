from services.inventory_service import InventoryService
from services.report_service import ReportService

def main():
    print("=== HỆ THỐNG WAREHOUSE INVENTORY MANAGEMENT ===\n")
    
    # Khởi tạo các Service
    inv_service = InventoryService()
    report_service = ReportService(inv_service)
    
    # Dữ liệu mẫu ban đầu
    print("[Hệ thống] Đang nạp dữ liệu mẫu...")
    inv_service.import_product("P001", "Sữa tươi Vinamilk", 100, "2026-06-01")
    inv_service.import_product("P002", "Bánh mì gối", 50, "2026-05-20")
    inv_service.import_product("P003", "Nước mắm", 200, "2027-01-01")
    inv_service.add_order("ORD001", "Nguyễn Văn A", "P001", 10)
    inv_service.add_order("ORD002", "Trần Thị B", "P002", 5)

    # Vòng lặp menu chính
    while True:
        print("\n" + "="*45)
        print("                  MENU CHÍNH                 ")
        print("="*45)
        print("[1] Nhập hàng mới")
        print("[2] Tra cứu sản phẩm")
        print("[3] Xem báo cáo cảnh báo cận date")
        print("[4] Xuất hàng tự động (FEFO)")
        print("[5] Hiển thị TẤT CẢ sản phẩm")
        print("[6] Hoàn tác thao tác gần nhất (Undo)")
        print("[7] Hiển thị hàng đã xuất khỏi kho")
        print("[8] Hiển thị đơn hàng đang xử lý (Khách đặt)")
        print("[9] Xem tổng số đơn chờ")
        print("[0] Thoát hệ thống")
        print("="*45)
        
        choice = input("Mời cậu chọn tác vụ (0-8): ").strip()
        
        match choice:
            case '1':
                print("\n--- NHẬP HÀNG ---")
                try:
                    p_id = input("Nhập mã sản phẩm (VD: P004): ").strip()
                    p_name = input("Nhập tên sản phẩm: ").strip()
                    p_qty = int(input("Nhập số lượng: "))
                    p_date = input("Nhập HSD (YYYY-MM-DD): ").strip()
                    inv_service.import_product(p_id, p_name, p_qty, p_date)
                except ValueError:
                    print("[LỖI] Dữ liệu nhập không hợp lệ. Số lượng phải là số nguyên!")
                except Exception as e:
                    print(f"[LỖI] Sai định dạng: {e}")

            case '2':
                print("\n--- TRA CỨU ---")
                p_id = input("Nhập mã sản phẩm cần tìm: ").strip()
                inv_service.search_product(p_id)

            case '3':
                print("\n--- CẢNH BÁO CẬN DATE ---")
                try:
                    days = int(input("Nhập ngưỡng số ngày cảnh báo (VD: 30): "))
                    report_service.generate_expiry_report(days_threshold=days)
                except ValueError:
                    print("[LỖI] Số ngày phải là một số nguyên!")

            case '4':
                print("\n--- XUẤT HÀNG (FEFO) ---")
                inv_service.export_fefo()

            case '5':
                print("\n--- XEM KHO HÀNG ---")
                inv_service.display_all_products()

            case '6':
                print("\n--- HOÀN TÁC (UNDO) ---")
                result = inv_service.undo_last_action()
                print(result.get("message", result))

            case '7':
                print("\n--- HÀNG ĐÃ XUẤT KHỎI KHO ---")
                exported = inv_service.display_exported_products()
                if not exported:
                    print("Chưa có kiện hàng nào được xuất khỏi kho.")
                else:
                    for i, item in enumerate(exported, 1):
                        exported_at = item.get('exported_at', '—')
                        print(f"  [{i}] {item['product_id']} | {item['name']} | SL: {item['quantity']} | HSD: {item['expiry_date']} | Xuất lúc: {exported_at}")

            case '8':
                print("\n--- ĐƠN HÀNG ĐANG XỬ LÝ (QUEUE) ---")
                orders = inv_service.get_pending_orders()
                if not orders:
                    print("Hàng đợi rỗng. Chưa có đơn hàng nào cần xử lý.")
                else:
                    for i, o in enumerate(orders, 1):
                        print(f"  [{i}] Mã Đơn: {o['order_id']} | Khách: {o['customer_name']} | Mã SP: {o['product_id']} | SL: {o['quantity']} | Trạng thái: {o['status']}")

            case '9':
                print("\n--- TỔNG SỐ ĐƠN CHỜ ---")
                count = inv_service.get_pending_orders_count()
                print(f"Hiện đang có {count} đơn hàng chờ xử lý trong hàng đợi.")

            case '0':
                print("\nĐang đóng hệ thống. Tạm biệt cậu!")
                break

            case _:
                print("\n[LỖI] Lựa chọn không hợp lệ, vui lòng bấm từ 0 đến 9!")

if __name__ == "__main__":
    main()