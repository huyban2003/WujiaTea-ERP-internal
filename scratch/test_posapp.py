import sys
import os
import time

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
    print("Kết quả Login:", login_res)
    
    print("\n=== 2. Test get_orders_by_date_ranges (Chạy song song đa luồng) ===")
    date_ranges = [
        ('2026-07-01', '2026-07-31'),
        ('2026-06-01', '2026-06-30'),
        ('2026-05-01', '2026-05-31'),
    ]
    
    start_time = time.time()
    result = client.get_orders_by_date_ranges(
        date_ranges=date_ranges,
        shop_code='H004',
        max_workers=3
    )
    elapsed = time.time() - start_time
    
    print(f"\nThời gian chạy song song: {elapsed:.2f} giây")
    print("Kết quả data_groups:")
    for group in result:
        print(group)

if __name__ == "__main__":
    main()
