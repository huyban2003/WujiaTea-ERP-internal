import sys
import os

# Add the directory containing posapp_client.py directly to sys.path
# This avoids triggering wujia_franchise/__init__.py (which imports Odoo models requiring the odoo package)
current_dir = os.path.dirname(os.path.abspath(__file__))
models_dir = os.path.abspath(os.path.join(current_dir, '..', 'custom', 'wujia_franchise', 'models'))
sys.path.insert(0, models_dir)

# pyrefly: ignore [missing-import]
from posapp_client import PosAppClient

def main():
    print("=== Khởi tạo PosAppClient ===")
    client = PosAppClient()
    
    print("\n=== 1. Test system_login API ===")
    login_res = client.system_login()
    print("Kết quả Login:")
    print(login_res)
    
    print("\n=== 2. Test get_orders_by_payment_status API ===")
    orders_res = client.get_orders_by_payment_status(
        date_start='2026-07-01',
        date_end='2026-07-31',
        shop_code='H004',
    )
    print("Kết quả Orders (Trích đoạn):")
    print(str(orders_res)[:500])

if __name__ == "__main__":
    main()
