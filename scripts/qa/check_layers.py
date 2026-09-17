#!/usr/bin/env python3
"""Kiểm luật tầng module ADR-027 trên __manifest__.py của custom/wujia_* — chỉ báo, exit 0.

    python3 scripts/qa/check_layers.py
    python3 scripts/qa/check_layers.py --json out.json
    python3 scripts/qa/check_layers.py --strict      # exit 1 nếu có vi phạm (dùng sau khi mục D chốt)

Tầng (ADR-027, chapter 74):
  L1  wujia_core (+ wujia_ui_core, *_core platform)
  L2  nghiệp vụ  — wujia_sale, _fleet, _delivery, _account, _franchise*
  L2  khung kênh — wujia_portal_layout | wujia_mobile_core
  L3a wujia_portal_base (nền ghép portal)
  L3b wujia_portal_<chức năng> | wujia_mobile_<x>

Module mới chưa khai trong LAYER thì báo `chưa phân tầng` — thêm vào bảng, đừng đoán theo tên.
"""
import argparse
import ast
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CUSTOM = ROOT / 'custom'

CORE, BIZ, FRAME, BASE, CHANNEL = 'L1 core', 'L2 nghiệp vụ', 'L2 khung', 'L3a portal_base', 'L3b ghép'

LAYER = {
    'wujia_core': CORE,
    'wujia_sale': BIZ, 'wujia_fleet': BIZ, 'wujia_delivery': BIZ, 'wujia_account': BIZ,
    'wujia_franchise': BIZ, 'wujia_franchise_contract': BIZ,
    'wujia_franchise_inspection': BIZ, 'wujia_franchise_operations': BIZ,
    'wujia_portal_layout': FRAME, 'wujia_mobile_core': FRAME,
    'wujia_portal_base': BASE,
}

# 7 portal_* đang ôm model nghiệp vụ, chờ tách ở F7–F13 (plan cụm F §1.A1)
PENDING_SPLIT = {
    'wujia_portal_order_window', 'wujia_portal_info_request', 'wujia_portal_knowledge',
    'wujia_portal_support', 'wujia_portal_notification', 'wujia_portal_exam', 'wujia_portal_return',
}

THAI = {
    'wujia_franchise', 'wujia_franchise_contract', 'wujia_franchise_inspection',
    'wujia_franchise_operations', 'wujia_portal_inspection', 'wujia_mobile_core',
}


def layer_of(name):
    if name in LAYER:
        return LAYER[name]
    if name.startswith(('wujia_portal_', 'wujia_mobile_')):
        return CHANNEL
    return None


def channel_of(name):
    if name.startswith('wujia_portal_') or name == 'wujia_portal_layout':
        return 'portal'
    if name.startswith('wujia_mobile_'):
        return 'mobile'
    return None


def load_manifests():
    out = {}
    for mf in sorted(CUSTOM.glob('wujia_*/__manifest__.py')):
        data = ast.literal_eval(mf.read_text(encoding='utf-8'))
        out[mf.parent.name] = [d for d in data.get('depends', [])]
    return out


def closure(name, deps, seen=None):
    seen = set() if seen is None else seen
    for d in deps.get(name, []):
        if d not in seen:
            seen.add(d)
            closure(d, deps, seen)
    return seen


def check(deps):
    violations, unknown = [], []
    for mod, direct in deps.items():
        lay = layer_of(mod)
        if lay is None:
            unknown.append(mod)
            continue
        wj = [d for d in direct if d in deps]
        for d in wj:
            dl = layer_of(d)
            rule = None
            if lay in (CORE, BIZ) and dl in (FRAME, BASE, CHANNEL):
                rule = 'R1 nghiệp vụ/core không depend khung hay module ghép'
            elif lay == FRAME and dl in (BIZ, BASE, CHANNEL):
                rule = 'R2 khung không depend nghiệp vụ/ghép'
            elif lay == FRAME and dl == FRAME:
                rule = 'R3 hai khung kênh không depend nhau'
            elif lay in (BASE, CHANNEL) and channel_of(mod) and channel_of(d) and channel_of(mod) != channel_of(d):
                rule = 'R3 portal_* ↔ mobile_* không depend chéo'
            elif lay == BASE and dl == CHANNEL:
                rule = 'R5 portal_base không depend portal_<x>'
            if rule:
                violations.append({'module': mod, 'depends': d, 'rule': rule})
        if lay == CHANNEL and channel_of(mod) == 'portal' and 'wujia_portal_base' not in closure(mod, deps):
            violations.append({'module': mod, 'depends': '(thiếu) wujia_portal_base', 'rule': 'R4 mọi portal_<x> depend portal_base'})
    for v in violations:
        v['owner'] = 'Thái' if v['module'] in THAI or v['depends'] == 'wujia_mobile_core' else 'Dev portal'
        v['note'] = 'chờ tách F7–F13' if v['module'] in PENDING_SPLIT else ('mục D, chờ chốt với anh Thái' if v['depends'] == 'wujia_mobile_core' else '')
    return violations, unknown


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--json')
    ap.add_argument('--strict', action='store_true')
    args = ap.parse_args()

    deps = load_manifests()
    violations, unknown = check(deps)

    print(f'# check_layers — {len(deps)} module wujia_*, {len(violations)} vi phạm\n')
    for lay in (CORE, BIZ, FRAME, BASE, CHANNEL):
        mods = [m for m in deps if layer_of(m) == lay]
        print(f'{lay:16} {len(mods):2}  ' + ', '.join(mods))
    if unknown:
        print(f'\nchưa phân tầng: {", ".join(unknown)}')
    print('\n| Module | Depend | Luật | Chủ code | Ghi chú |\n|---|---|---|---|---|')
    for v in violations:
        print(f"| `{v['module']}` | `{v['depends']}` | {v['rule']} | {v['owner']} | {v['note']} |")
    if args.json:
        pathlib.Path(args.json).write_text(json.dumps({'violations': violations, 'unknown': unknown}, ensure_ascii=False, indent=2))
    return 1 if args.strict and (violations or unknown) else 0


if __name__ == '__main__':
    sys.exit(main())
