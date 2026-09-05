#!/usr/bin/env python3
"""Fetch + parse a ChatGPT *share* link (BA controller spec) → Markdown.

Vì sao cần tool này: từ Sprint 30 trở đi, MỌI spec controller BA gửi đều nằm trong 1 chat
ChatGPT share. Trang share render bằng JS (react-router v7 / turbo-stream) → curl thô hoặc
`backend-api/share/<id>` bị Cloudflare 403. Cách chạy được: tải HTML page với User-Agent
trình duyệt, bóc các chunk `streamController.enqueue("…")`, decode JS-string, rồi lấy các
message string trong mảng phẳng turbo-stream.

Dev-only — KHÔNG thuộc module Odoo nào, KHÔNG chạy trên server (thư mục này gitignored).

Dùng:
    python3 fetch_ba_chat.py <share_url> [-o out.md] [--min-len 60]
    python3 fetch_ba_chat.py https://chatgpt.com/share/6a54f1b6-... -o /tmp/ba.md
"""
import argparse
import json
import re
import sys
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/125.0 Safari/537.36")
# Keyword giữ lại cả câu ngắn nếu chứa từ khoá controller (không chỉ lọc theo độ dài).
KEEP_KW = ('thông báo', 'notification', 'controller', 'priority', 'route',
           'model', 'field', 'filter', 'validation', 'error', 'mapping')


def fetch_html(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': UA,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', 'ignore')


def extract_blob(html):
    """Ghép các chunk react-router stream (JS-escaped) thành 1 blob turbo-stream phẳng."""
    chunks = re.findall(r'streamController\.enqueue\("((?:[^"\\]|\\.)*)"\)', html)
    blob = ''
    for c in chunks:
        try:
            blob += json.loads('"' + c + '"')
        except Exception:
            blob += bytes(c, 'utf-8').decode('unicode_escape', 'ignore')
    return blob


def _decode(s):
    try:
        return json.loads('"' + s + '"')
    except Exception:
        return s.encode().decode('unicode_escape', 'ignore')


def extract_messages(blob, min_len=60):
    """Turbo-stream dedup string vào mảng phẳng → bóc mọi string 'giống nội dung message'."""
    out, seen = [], set()
    for raw in re.findall(r'"((?:[^"\\]|\\.)*)"', blob):
        d = _decode(raw).strip()
        if not d or d in seen:
            continue
        if len(d) >= min_len or any(k in d.lower() for k in KEEP_KW):
            if not d.startswith('http') and 'assets/' not in d:
                seen.add(d)
                out.append(d)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('url', help='ChatGPT share URL (chatgpt.com/share/<id>)')
    ap.add_argument('-o', '--out', help='ghi Markdown ra file (mặc định: stdout)')
    ap.add_argument('--min-len', type=int, default=60,
                    help='độ dài tối thiểu string giữ lại (mặc định 60)')
    args = ap.parse_args()

    html = fetch_html(args.url)
    blob = extract_blob(html)
    if 'linear_conversation' not in html and not blob:
        sys.exit('!! Không thấy dữ liệu conversation — link private/hết hạn hoặc CF chặn.')
    msgs = extract_messages(blob, args.min_len)
    if not msgs:
        sys.exit('!! Parse ra 0 message — kiểm tra lại link share.')
    md = ('\n\n=====\n\n'.join(msgs))
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(md)
        print(f'OK — {len(msgs)} message blocks → {args.out}')
    else:
        print(md)


if __name__ == '__main__':
    main()
