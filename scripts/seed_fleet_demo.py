"""Seed dữ liệu demo cho wujia_fleet + wujia_delivery vào DB local.

Mục đích: tạo records trực tiếp trong DB dev để test giao diện, KHÔNG được
load như Odoo demo data (tránh đẩy lên server).

Cách chạy:
    cd /home/huyban/odoo-dev/WujiaTea/odoo19
    /home/huyban/miniconda3/envs/odoo/bin/python odoo-bin shell \\
        -c /home/huyban/odoo-dev/WujiaTea/config/odoo.conf \\
        -d wujia_tea_19 --no-http \\
        < /home/huyban/odoo-dev/WujiaTea/scripts/seed_fleet_demo.py

Idempotent: chạy nhiều lần không tạo trùng (lookup theo `code`).
"""
print("=== SEEDING WUJIA_FLEET + WUJIA_DELIVERY DEMO DATA ===")


def upsert(model_name, search_domain, vals, label):
    Model = env[model_name]
    rec = Model.search(search_domain, limit=1)
    if rec:
        rec.write(vals)
        print(f"  [UPDATE] {label}: {rec.display_name or rec.id}")
    else:
        rec = Model.create(vals)
        print(f"  [CREATE] {label}: {rec.display_name or rec.id}")
    return rec


# ============================================================
# 1) Demo areas (nếu chưa có) — wujia_portal_base.area_hcm_q1 / area_hn_central
# ============================================================
print("\n[1] Areas (lookup hoặc tạo)")
area_hcm = env.ref('wujia_portal_base.area_hcm_q1', raise_if_not_found=False)
if not area_hcm:
    area_hcm = upsert(
        'res.area', [('code', '=', 'KV-HCM-01')],
        {'code': 'KV-HCM-01', 'name': 'TP HCM Quận 1-3', 'sequence': 10},
        'area HCM',
    )
area_hn = env.ref('wujia_portal_base.area_hn_central', raise_if_not_found=False)
if not area_hn:
    area_hn = upsert(
        'res.area', [('code', '=', 'KV-HN-01')],
        {'code': 'KV-HN-01', 'name': 'Hà Nội Trung tâm', 'sequence': 20},
        'area HN',
    )

# ============================================================
# 2) Fleet Providers
# ============================================================
print("\n[2] Fleet Providers")
provider_internal = upsert(
    'wujia.fleet.provider', [('code', '=', 'WJ-INT')],
    {
        'code': 'WJ-INT',
        'name': 'Wujia Internal Fleet',
        'provider_type': 'company',
        'contact_name': 'Anh Nam',
        'phone': '0901234567',
        'email': 'fleet@wujia.local',
        'description': 'Đội xe nội bộ Wujia, dùng cho tuyến cố định nội thành HCM.',
    },
    'provider WJ-INT',
)
provider_ndung = upsert(
    'wujia.fleet.provider', [('code', '=', 'NDUNG')],
    {
        'code': 'NDUNG',
        'name': 'CTY TNHH Vận Tải Nguyễn Dũng',
        'provider_type': 'outsource',
        'contact_name': 'Anh Dũng',
        'phone': '0987654321',
        'email': 'dung.ndvtl@gmail.com',
        'description': 'Nhà xe thuê ngoài, chuyên tuyến đi tỉnh.',
    },
    'provider NDUNG',
)

# ============================================================
# 3) Fleet Types
# ============================================================
print("\n[3] Fleet Types")
type_p09 = upsert('wujia.fleet.type', [('code', '=', 'P09')],
    {'code': 'P09', 'name': 'Bán tải 0.9T', 'vehicle_category': 'pickup', 'payload_capacity_ton': 0.9, 'sequence': 10},
    'type P09')
type_t19 = upsert('wujia.fleet.type', [('code', '=', 'T19')],
    {'code': 'T19', 'name': 'Xe tải 1.9T', 'vehicle_category': 'truck', 'payload_capacity_ton': 1.9, 'sequence': 20},
    'type T19')
type_t35 = upsert('wujia.fleet.type', [('code', '=', 'T35')],
    {'code': 'T35', 'name': 'Xe tải 3.5T', 'vehicle_category': 'truck', 'payload_capacity_ton': 3.5, 'sequence': 30},
    'type T35')
type_f17 = upsert('wujia.fleet.type', [('code', '=', 'F17')],
    {'code': 'F17', 'name': 'Xe đông lạnh 17T', 'vehicle_category': 'truck', 'payload_capacity_ton': 17.0, 'sequence': 40},
    'type F17')

# ============================================================
# 4) Vehicles
# ============================================================
print("\n[4] Vehicles")
upsert('wujia.fleet.management', [('code', '=', 'V001')],
    {'code': 'V001', 'name': '51C-12345 — Bán tải 0.9T', 'provider_id': provider_internal.id,
     'fleet_type_id': type_p09.id, 'license_plate': '51C-12345', 'driver_name': 'Trần Văn A',
     'driver_phone': '0911222333', 'vehicle_status': 'available'}, 'vehicle V001')
upsert('wujia.fleet.management', [('code', '=', 'V002')],
    {'code': 'V002', 'name': '51C-23456 — Tải 1.9T', 'provider_id': provider_internal.id,
     'fleet_type_id': type_t19.id, 'license_plate': '51C-23456', 'driver_name': 'Lê Văn B',
     'driver_phone': '0911222334', 'vehicle_status': 'available'}, 'vehicle V002')
upsert('wujia.fleet.management', [('code', '=', 'V101')],
    {'code': 'V101', 'name': '51C-34567 — Tải 3.5T (Nguyễn Dũng)', 'provider_id': provider_ndung.id,
     'fleet_type_id': type_t35.id, 'license_plate': '51C-34567', 'driver_name': 'Phạm Văn C',
     'driver_phone': '0911222335', 'vehicle_status': 'available'}, 'vehicle V101')
upsert('wujia.fleet.management', [('code', '=', 'V102')],
    {'code': 'V102', 'name': '51C-45678 — Tải 3.5T (Nguyễn Dũng)', 'provider_id': provider_ndung.id,
     'fleet_type_id': type_t35.id, 'license_plate': '51C-45678', 'driver_name': 'Đặng Văn D',
     'driver_phone': '0911222336', 'vehicle_status': 'available'}, 'vehicle V102')
upsert('wujia.fleet.management', [('code', '=', 'V103')],
    {'code': 'V103', 'name': '51C-99999 — Đông lạnh 17T', 'provider_id': provider_ndung.id,
     'fleet_type_id': type_f17.id, 'license_plate': '51C-99999', 'driver_name': 'Hoàng Văn E',
     'driver_phone': '0911222337', 'vehicle_status': 'maintenance'}, 'vehicle V103')

# ============================================================
# 5) Pricelist + lines
# ============================================================
print("\n[5] Pricelist + lines")
pl = upsert('wujia.fleet.pricelist', [('code', '=', 'PL-T35-2026')],
    {'code': 'PL-T35-2026', 'name': 'Cước phí Tải 3.5T 2026',
     'fleet_type_id': type_t35.id, 'provider_id': provider_ndung.id,
     'trip_scope': 'interprovince', 'default_drop_fee': 50000,
     'date_from': '2026-01-01', 'date_to': '2026-12-31', 'state': 'active'},
    'pricelist PL-T35-2026')
# Reset lines + recreate idempotent
pl.line_ids.unlink()
env['wujia.fleet.pricelist.line'].create([
    {'pricelist_id': pl.id, 'sequence': 10, 'area_ids': [(6, 0, [area_hcm.id])],
     'price': 800000, 'drop_fee': 50000, 'note': 'Nội thành HCM Q1'},
    {'pricelist_id': pl.id, 'sequence': 20, 'area_ids': [(6, 0, [area_hn.id])],
     'price': 2500000, 'drop_fee': 100000, 'note': 'Hà Nội trung tâm — đi tỉnh'},
])
print(f"  Pricelist {pl.code} có {len(pl.line_ids)} line")

env.cr.commit()
print("\n=== DONE — đã commit vào DB local ===")
