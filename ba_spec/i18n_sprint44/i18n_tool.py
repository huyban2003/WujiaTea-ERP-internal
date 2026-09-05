#!/usr/bin/env python3
"""Sprint 44 — trích / áp chuỗi tiếng Việt của BACKEND (không đụng portal).

extract : quét file backend, in ra JSON các chuỗi Việt duy nhất theo từng loại vị trí.
apply   : đọc map vi->en, thay TẠI CHỖ đúng những vị trí đã trích (không sed toàn cục).

Vị trí được coi là "nhãn backend":
  XML  attr : string= help= confirm= placeholder= (+ <menuitem name=>)
  XML  node : <field name="name"> của act_window/menuitem/res.groups/ir.rule,
              text thuần trong <t t-name="card"> và trong help html
  PY        : string='..' help='..' _description='..' + nhãn trong Selection([...])
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path("/home/huyban/odoo-dev/WujiaTea/custom")
MAP_FILE = Path(__file__).with_name("vi_en_map.json")

VN = "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
VN += VN.upper()
HAS_VN = re.compile(f"[{VN}]")

# Module trong phạm vi (bỏ wj_ks_* — đã English, workstream riêng)
MODULES = [
    "wujia_core", "wujia_delivery", "wujia_fleet", "wujia_franchise", "wujia_sale",
    "wujia_portal_base", "wujia_portal_debt", "wujia_portal_delivery",
    "wujia_portal_exam", "wujia_portal_info_request", "wujia_portal_knowledge",
    "wujia_portal_layout", "wujia_portal_notification", "wujia_portal_order_window",
    "wujia_portal_purchase_history", "wujia_portal_report", "wujia_portal_return",
    "wujia_portal_sale", "wujia_portal_support",
]

# Basename XML là template PORTAL -> loại trừ tuyệt đối
PORTAL_XML = re.compile(
    r"^(portal_.*|mobile_.*|pc_.*|.*sidenav.*|.*_inherit|login_page|profile_page|"
    r"change_password_page|layouts|templates|store_picker.*|wj_page_header|assets|"
    r".*_in_layout|home_kpi.*|bottomnav.*)\.xml$"
)


def xml_files():
    for m in MODULES:
        for f in sorted((ROOT / m).rglob("*.xml")):
            if "/data/" in str(f):          # dữ liệu nghiệp vụ hiện trên portal -> out of scope
                continue
            if PORTAL_XML.match(f.name):
                continue
            yield f


def py_files():
    for m in MODULES:
        for sub in ("models", "wizards", "report"):
            for f in sorted((ROOT / m / sub).rglob("*.py")):
                yield f


# ---------------------------------------------------------------- extract
ATTR_RE = re.compile(r'\b(string|help|confirm|placeholder)="([^"]*)"')
MENU_NAME_RE = re.compile(r'(<menuitem\b[^>]*?\bname=")([^"]*)(")', re.S)
FIELD_NAME_RE = re.compile(r'(<field name="name">)([^<]*)(</field>)')
TEXT_NODE_RE = re.compile(r'>([^<>{}]+)<')

# KHÔNG re.S: nhãn luôn nằm trên 1 dòng. Bật re.S là regex nuốt xuyên dòng,
# trích ra nguyên khối code (đã dính bug này 1 lần).
PY_KW_RE = re.compile(r"\b(?:string|help)=(['\"])([^'\"\n]*)\1")
PY_DESC_RE = re.compile(r"_description\s*=\s*(['\"])([^'\"\n]*)\1")
PY_SEL_RE = re.compile(r"\(\s*(['\"])[a-z0-9_]+\1\s*,\s*(['\"])([^'\"\n]*)\2\s*\)")


def extract():
    found = {}

    def add(s, where):
        s = s.strip()
        if s and HAS_VN.search(s):
            found.setdefault(s, []).append(where)

    for f in xml_files():
        txt = f.read_text(encoding="utf-8")
        rel = str(f.relative_to(ROOT))
        for _, v in ATTR_RE.findall(txt):
            add(v, rel)
        for _, v, _ in MENU_NAME_RE.findall(txt):
            add(v, rel)
        for _, v, _ in FIELD_NAME_RE.findall(txt):
            add(v, rel)
        for v in TEXT_NODE_RE.findall(txt):
            add(v, rel)

    for f in py_files():
        txt = f.read_text(encoding="utf-8")
        rel = str(f.relative_to(ROOT))
        for _, v in PY_KW_RE.findall(txt):
            add(v, rel)
        for _, v in PY_DESC_RE.findall(txt):
            add(v, rel)
        for _, _, v in PY_SEL_RE.findall(txt):
            add(v, rel)

    out = {k: sorted(set(v)) for k, v in sorted(found.items())}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    print(f"\n# {len(out)} chuỗi duy nhất", file=sys.stderr)


# ---------------------------------------------------------------- apply
def apply_map(dry=True):
    mapping = json.loads(MAP_FILE.read_text(encoding="utf-8"))
    missing, changed = {}, 0

    def tr(v, rel):
        nonlocal changed
        s = v.strip()
        if not s or not HAS_VN.search(s):
            return None
        if s not in mapping:
            missing.setdefault(s, set()).add(rel)
            return None
        changed += 1
        return v.replace(s, mapping[s])

    for f in list(xml_files()) + list(py_files()):
        txt = orig = f.read_text(encoding="utf-8")
        rel = str(f.relative_to(ROOT))

        if f.suffix == ".xml":
            def sub_attr(m):
                new = tr(m.group(2), rel)
                return f'{m.group(1)}="{new}"' if new is not None else m.group(0)
            txt = ATTR_RE.sub(sub_attr, txt)

            def sub_grp(m):
                new = tr(m.group(2), rel)
                return m.group(1) + new + m.group(3) if new is not None else m.group(0)
            txt = MENU_NAME_RE.sub(sub_grp, txt)
            txt = FIELD_NAME_RE.sub(sub_grp, txt)

            def sub_text(m):
                new = tr(m.group(1), rel)
                return ">" + new + "<" if new is not None else m.group(0)
            txt = TEXT_NODE_RE.sub(sub_text, txt)
        else:
            def sub_py(m):
                new = tr(m.group(2), rel)
                if new is None:
                    return m.group(0)
                return m.group(0).replace(m.group(2), new)
            txt = PY_KW_RE.sub(sub_py, txt)
            txt = PY_DESC_RE.sub(sub_py, txt)

            def sub_sel(m):
                new = tr(m.group(3), rel)
                if new is None:
                    return m.group(0)
                return m.group(0).replace(m.group(3), new)
            txt = PY_SEL_RE.sub(sub_sel, txt)

        if txt != orig and not dry:
            f.write_text(txt, encoding="utf-8")

    if missing:
        print(f"!! {len(missing)} chuỗi CHƯA có trong map — dừng, không ghi im lặng:")
        for s, files in sorted(missing.items())[:40]:
            print(f"   {s!r}  <- {sorted(files)[0]}")
        sys.exit(2)
    print(f"{'[dry-run] ' if dry else ''}đã dịch {changed} vị trí, 0 chuỗi thiếu map")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "extract"
    if cmd == "extract":
        extract()
    else:
        apply_map(dry=(cmd != "apply"))
