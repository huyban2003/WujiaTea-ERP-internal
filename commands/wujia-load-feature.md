---
description: Extract BA spec for one or more WujiaTea feature letters (A–G) and brief Claude on it
argument-hint: <LETTER> [LETTER ...]   e.g. /wujia-load-feature C E
---

You are loading the BA spec for feature letter(s): **$ARGUMENTS**

Do these steps in order:

**Step 1.** Run the extractor (it parses `WujiaTea/docs/Wujia_Internal ERP Master Plan.xlsm` and dumps markdown):

```bash
python3 /home/huyban/odoo-dev/scripts/wujia_extract_feature.py $ARGUMENTS
```

The script will print:
- For each letter: row range in "1. Model Field", a markdown table of model fields, and a markdown table of FEATURE CHECKLIST rows (Feature ID `<LETTER>.*`).
- If multiple letters → multiple `## Feature X` sections.
- At the end: an excerpt from "2. FE - Portal" (first 80 rows) for portal context.

**Step 2.** Read the output carefully, then summarize back to user in 5–8 bullets:
- Feature name(s) (from the section header like `C. Knowledge & Helpdesk`)
- Number of models per feature (count distinct values in "Model" column)
- Models that already exist in `/home/huyban/odoo-dev/WujiaTea/custom/` (cross-check with `ls custom/` if needed)
- Any "Module" column value in FEATURE CHECKLIST that's marked Done vs Pending
- Top 3 risky/non-trivial fields (relations, computed, constraints)
- Portal-facing items? (any row in "2. FE - Portal" that mentions this feature)

**Step 3.** Ask the user **one** of these (choose based on context):
- Nếu feature đã có module → "Tôi review BA và so với module hiện tại. Anh muốn tôi (a) báo gap chỗ nào, (b) implement thẳng phần thiếu, hay (c) chỉ trả lời câu hỏi cụ thể?"
- Nếu feature chưa có module → "Tôi sẽ scaffold module mới. Anh confirm tên module và Sprint chứa nó: `wujia_<...>` thuộc Sprint <N>?"
- Nếu nhiều letter cùng lúc và scope rộng → "Tôi split thành sub-tasks cho từng letter, anh duyệt thứ tự nào trước?"

**Step 4.** Wait for user's answer trước khi viết code.

---

**Why this command exists:**

BA spec sheet `1. Model Field` có 1044 dòng, 7 feature letter (A–G). Đọc thẳng xlsm trong session tốn ~10k token mỗi lần. Script này lọc chính xác rows thuộc feature anh quan tâm + cross-reference với FEATURE CHECKLIST + portal sheet, đầu ra ~1-3k token tùy feature. Claude chỉ nắm phần liên quan, không nhồi cả sheet.

**Caveat:** script đọc `data_only=True` nên formula trong xlsm trả về giá trị cached (nếu file xlsm chưa từng được mở+save trong Excel/LibreOffice sau khi sửa formula → giá trị có thể là None). Trường hợp đó: mở file một lần trong LibreOffice và save, hoặc đọc thẳng cell.value bằng `data_only=False`.
