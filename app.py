from flask import Flask, render_template, request, jsonify
from services.inventory_service import InventoryService
from services.report_service import ReportService

app = Flask(__name__)

# Khởi tạo Services
inv_service = InventoryService()
report_service = ReportService(inv_service)

# Nạp dữ liệu mẫu ban đầu
inv_service.import_product("P001", "Sữa tươi Vinamilk", 100, "2026-06-01")
inv_service.import_product("P002", "Bánh mì gối", 50, "2026-05-20")
inv_service.import_product("P003", "Nước mắm", 200, "2027-01-01")
inv_service.import_product("P004", "Thịt bò Kobe", 20, "2026-06-15")
inv_service.import_product("P005", "Rau cải thìa", 100, "2026-06-10")
inv_service.import_product("P006", "Sữa chua", 50, "2026-05-15") # Quá hạn
inv_service.add_order("ORD001", "Nguyễn Văn A", "P001", 10)
inv_service.add_order("ORD002", "Trần Thị B", "P002", 5)
inv_service.add_order("ORD003", "Lê Văn C", "P006", 10)

# --- Routes cho Giao diện UI ---
@app.route('/')
def index():
    return render_template('index.html')

# --- API Endpoints ---
@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    products = inv_service.display_all_products()
    return jsonify({"status": "success", "data": products})

@app.route('/api/inventory/import', methods=['POST'])
def import_product():
    data = request.json
    try:
        product_id = data.get('product_id')
        name = data.get('name')
        quantity = int(data.get('quantity'))
        expiry_date = data.get('expiry_date')
        
        result = inv_service.import_product(product_id, name, quantity, expiry_date)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/inventory/export-fifo', methods=['POST'])
def export_fifo():
    result = inv_service.export_fifo()
    return jsonify(result)

@app.route('/api/inventory/search/<product_id>', methods=['GET'])
def search_product(product_id):
    result = inv_service.search_product(product_id)
    return jsonify(result)

@app.route('/api/inventory/exported', methods=['GET'])
def get_exported_products():
    products = inv_service.display_exported_products()
    return jsonify({"status": "success", "data": products})

@app.route('/api/inventory/undo', methods=['POST'])
def undo_action():
    result = inv_service.undo_last_action()
    return jsonify(result)

@app.route('/api/orders', methods=['GET'])
def get_orders():
    orders = inv_service.get_pending_orders()
    return jsonify({"status": "success", "data": orders})

@app.route('/api/orders', methods=['POST'])
def add_order():
    data = request.json
    try:
        order_id = data.get('order_id')
        customer_name = data.get('customer_name')
        product_id = data.get('product_id')
        quantity = int(data.get('quantity'))
        
        result = inv_service.add_order(order_id, customer_name, product_id, quantity)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/api/reports/expiry', methods=['GET'])
def get_expiry_report():
    days_threshold = request.args.get('days', default=30, type=int)
    report_data = report_service.generate_expiry_report(days_threshold)
    return jsonify({"status": "success", "data": report_data})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
