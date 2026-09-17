import re
def strip_comments_keep_len(s):
    return re.sub(r'/\*.*?\*/', lambda m: re.sub(r'[^\n]', ' ', m.group(0)), s, flags=re.S)

def parse(text):
    """Return list of items: dict(kind='rule'|'at', start, end, sel, body, media, children)
    offsets into original text; comments blanked for scanning."""
    s = strip_comments_keep_len(text)
    def block(i, depth_media, end_char_pos):
        items = []
        while i < end_char_pos:
            # skip whitespace
            while i < end_char_pos and s[i].isspace(): i += 1
            if i >= end_char_pos: break
            if s[i] == '}':
                return items, i
            j = s.index('{', i)
            k = s.find(';', i)
            if s[i] == '@' and k != -1 and k < j:
                items.append(dict(kind='stmt', start=i, end=k+1)); i = k+1; continue
            head = s[i:j].strip()
            if head.startswith('@media') or head.startswith('@supports'):
                kids, close = block(j+1, depth_media+[head], end_char_pos)
                items.append(dict(kind='at', start=i, end=close+1, head=head, children=kids, hstart=i, bopen=j))
                i = close+1
            else:
                # find matching close (keyframes nested)
                d, p = 0, j
                while True:
                    if s[p] == '{': d += 1
                    elif s[p] == '}':
                        d -= 1
                        if d == 0: break
                    p += 1
                items.append(dict(kind='rule', start=i, end=p+1, sel=head, body=s[j+1:p], media=list(depth_media)))
                i = p+1
        return items, i
    items, _ = block(0, [], len(s))
    return items

def split_selectors(sel):
    parts, d, cur = [], 0, ''
    for c in sel:
        if c in '([': d += 1
        if c in ')]': d -= 1
        if c == ',' and d == 0:
            parts.append(cur.strip()); cur = ''
        else: cur += c
    parts.append(cur.strip())
    return [p for p in parts if p]

def decls(body):
    out = []
    for d in body.split(';'):
        if ':' in d:
            k, v = d.split(':', 1)
            out.append((k.strip().lower(), ' '.join(v.split())))
    return out

def classes(part):
    return set(re.findall(r'\.(-?[_a-zA-Z][\w-]*)', part))

def group(cls):
    return re.split(r'__|--', cls)[0]

def flat_rules(items, text):
    for it in items:
        if it['kind'] == 'rule': yield it
        elif it['kind'] == 'at':
            yield from flat_rules(it['children'], text)
