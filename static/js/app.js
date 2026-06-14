document.addEventListener('DOMContentLoaded', () => {
    // ---- Navigation / SPA Logic ----
    const navItems = document.querySelectorAll('.nav-item');
    const viewSections = document.querySelectorAll('.view-section');
    const viewTitle = document.getElementById('current-view-title');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            // Remove active classes
            navItems.forEach(n => n.classList.remove('active'));
            viewSections.forEach(v => v.classList.remove('active'));

            // Add active class
            item.classList.add('active');
            const targetView = item.getAttribute('data-view');
            document.getElementById(`view-${targetView}`).classList.add('active');
            viewTitle.textContent = item.querySelector('span').textContent;

            // Trigger data load if needed
            if (targetView === 'dashboard') loadInventory();
            if (targetView === 'report') loadReport();
            if (targetView === 'exported') loadExported();
            if (targetView === 'orders') loadOrders();
        });
    });

    // ---- Toast Notification System ----
    function showToast(message, type = 'success') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = type === 'success' ? '<i class="fa-solid fa-circle-check"></i>' : '<i class="fa-solid fa-circle-exclamation"></i>';
        toast.innerHTML = `${icon} <span>${message}</span>`;
        
        container.appendChild(toast);
        
        // Trigger reflow to start animation
        setTimeout(() => toast.classList.add('show'), 10);
        
        // Remove after 3s
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // ---- API Calls ----
    const API_BASE = '/api/inventory';

    // 1. Load Inventory (Dashboard)
    async function loadInventory() {
        try {
            const res = await fetch(API_BASE);
            const data = await res.json();
            
            const tbody = document.querySelector('#inventory-table tbody');
            tbody.innerHTML = '';
            
            if (data.data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align:center">Kho hiện đang trống!</td></tr>';
                document.getElementById('total-items').textContent = '0';
                return;
            }

            data.data.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${item.product_id}</strong></td>
                    <td>${item.name}</td>
                    <td>${item.quantity}</td>
                    <td>${item.expiry_date}</td>
                `;
                tbody.appendChild(tr);
            });
            document.getElementById('total-items').textContent = data.data.length;
        } catch (error) {
            showToast('Lỗi khi tải dữ liệu kho', 'error');
        }
    }

    // 2. Import Product
    const importForm = document.getElementById('form-import');
    importForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const payload = {
            product_id: document.getElementById('imp-id').value,
            name: document.getElementById('imp-name').value,
            quantity: document.getElementById('imp-qty').value,
            expiry_date: document.getElementById('imp-date').value,
        };

        try {
            const res = await fetch(`${API_BASE}/import`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            
            if (data.status === 'success') {
                showToast(data.message, 'success');
                importForm.reset();
            } else {
                showToast(data.message || 'Có lỗi xảy ra', 'error');
            }
        } catch (error) {
            showToast('Lỗi kết nối server', 'error');
        }
    });

    // 3. Search Product
    document.getElementById('btn-search-submit').addEventListener('click', async () => {
        const query = document.getElementById('search-input').value.trim();
        if (!query) return;

        const resultBox = document.getElementById('search-result-container');
        try {
            const res = await fetch(`${API_BASE}/search/${query}`);
            const data = await res.json();
            
            resultBox.classList.remove('hidden');
            if (data.status === 'success') {
                const p = data.product;
                let batchesHtml = '';
                if (p.batches && p.batches.length > 0) {
                    batchesHtml = '<ul style="margin-left: 20px; margin-top: 5px;">' + 
                        p.batches.map(b => `<li style="font-size: 13px; color: var(--text-secondary);">HSD: ${b.expiry_date} - SL: ${b.quantity}</li>`).join('') +
                        '</ul>';
                }
                
                resultBox.innerHTML = `
                    <h4><i class="fa-solid fa-check"></i> Tìm thấy sản phẩm</h4>
                    <div class="result-item"><strong>Mã SP:</strong> ${p.product_id}</div>
                    <div class="result-item"><strong>Tên:</strong> ${p.name}</div>
                    <div class="result-item"><strong>Tổng SL:</strong> ${p.quantity}</div>
                    <div class="result-item"><strong>Chi tiết các lô hàng:</strong> ${batchesHtml}</div>
                `;
            } else {
                resultBox.innerHTML = `<h4 style="color: var(--danger-color)"><i class="fa-solid fa-xmark"></i> ${data.message}</h4>`;
            }
        } catch (error) {
            showToast('Lỗi tìm kiếm', 'error');
        }
    });

    // 4. Report Expiry
    async function loadReport() {
        const days = document.getElementById('report-days').value || 30;
        try {
            const res = await fetch(`/api/reports/expiry?days=${days}`);
            const data = await res.json();
            
            const tbody = document.querySelector('#report-table tbody');
            tbody.innerHTML = '';
            
            if (data.data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align:center">Không có sản phẩm nào cận date trong ${days} ngày tới.</td></tr>`;
                return;
            }

            data.data.forEach(item => {
                // Determine badge color roughly
                const today = new Date();
                const exp = new Date(item.expiry_date);
                const diffTime = Math.abs(exp - today);
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
                
                let badgeClass = 'badge-success';
                let statusText = 'An toàn';
                if (exp < today) { badgeClass = 'badge-danger'; statusText = 'Đã hết hạn'; }
                else if (diffDays <= 7) { badgeClass = 'badge-danger'; statusText = 'Rất khẩn cấp'; }
                else if (diffDays <= days) { badgeClass = 'badge-warning'; statusText = 'Sắp hết hạn'; }

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${item.product_id}</strong></td>
                    <td>${item.name}</td>
                    <td>${item.quantity}</td>
                    <td>${item.expiry_date}</td>
                    <td><span class="badge ${badgeClass}">${statusText}</span></td>
                `;
                tbody.appendChild(tr);
            });
        } catch (error) {
            showToast('Lỗi tải báo cáo', 'error');
        }
    }

    document.getElementById('btn-gen-report').addEventListener('click', loadReport);

    // 5. Load Exported Products
    async function loadExported() {
        try {
            const res = await fetch(`${API_BASE}/exported`);
            const data = await res.json();

            const tbody = document.querySelector('#exported-table tbody');
            tbody.innerHTML = '';

            if (data.data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center">Chưa có kiện hàng nào được xuất khỏi kho.</td></tr>';
                document.getElementById('total-exported').textContent = '0';
                return;
            }

            data.data.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${item.product_id}</strong></td>
                    <td>${item.name}</td>
                    <td>${item.quantity}</td>
                    <td>${item.expiry_date}</td>
                    <td>${item.exported_at || '—'}</td>
                `;
                tbody.appendChild(tr);
            });
            document.getElementById('total-exported').textContent = data.data.length;
        } catch (error) {
            showToast('Lỗi khi tải danh sách hàng đã xuất', 'error');
        }
    }

    document.getElementById('btn-refresh-exported').addEventListener('click', loadExported);

    // 6. Load Orders (Queue)
    async function loadOrders() {
        try {
            const res = await fetch('/api/orders');
            const data = await res.json();

            const tbody = document.querySelector('#orders-table tbody');
            tbody.innerHTML = '';

            if (data.data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center">Hàng đợi rỗng. Không có đơn hàng nào chờ xử lý.</td></tr>';
                document.getElementById('total-orders').textContent = '0';
                return;
            }

            data.data.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${item.order_id}</strong></td>
                    <td>${item.customer_name}</td>
                    <td>${item.product_id}</td>
                    <td>${item.quantity}</td>
                    <td><span class="badge badge-warning">${item.status}</span></td>
                `;
                tbody.appendChild(tr);
            });
            document.getElementById('total-orders').textContent = data.data.length;
        } catch (error) {
            showToast('Lỗi khi tải danh sách đơn hàng', 'error');
        }
    }

    if (document.getElementById('btn-refresh-orders')) {
        document.getElementById('btn-refresh-orders').addEventListener('click', loadOrders);
    }

    // 7. Quick Actions (FIFO & Undo)
    document.getElementById('btn-export-fifo').addEventListener('click', async () => {
        try {
            const res = await fetch(`${API_BASE}/export-fifo`, { method: 'POST' });
            const data = await res.json();
            
            if (data.status === 'success') {
                showToast(data.message, 'success');
                if (document.getElementById('view-dashboard').classList.contains('active')) loadInventory();
                if (document.getElementById('view-exported').classList.contains('active')) loadExported();
            } else {
                showToast(data.message, 'error');
            }
        } catch (error) { showToast('Lỗi xuất hàng', 'error'); }
    });

    document.getElementById('btn-undo').addEventListener('click', async () => {
        try {
            const res = await fetch(`${API_BASE}/undo`, { method: 'POST' });
            const data = await res.json();
            
            if (data.status === 'success') {
                showToast(data.message, 'success');
                if (document.getElementById('view-dashboard').classList.contains('active')) loadInventory();
                if (document.getElementById('view-exported').classList.contains('active')) loadExported();
            } else {
                showToast(data.message, 'warning');
            }
        } catch (error) { showToast('Lỗi hoàn tác', 'error'); }
    });

    // Refresh Dashboard
    document.getElementById('btn-refresh').addEventListener('click', loadInventory);

    // Init Load
    loadInventory();
});
