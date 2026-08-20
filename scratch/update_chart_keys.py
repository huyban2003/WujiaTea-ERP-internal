# 1. Update CSV
csv_path = "/home/dev/WujiaTea-ERP-internal/custom/wujia_franchise/data/wujia_franchise_export.csv"
with open(csv_path, "r", encoding="utf-8-sig") as f:
    csv_text = f.read().rstrip()

chart_entries = """
label:wujia.franchise.inspection:chart_history_title,Lịch sử điểm số giám sát (10 đợt gần nhất),評核分數歷史紀錄（近10次）
label:wujia.franchise.inspection:chart_single_score,Điểm từng đợt,各次評核分數
label:wujia.franchise.inspection:chart_avg_score,Điểm trung bình,平均分數
label:wujia.franchise.inspection:chart_no_data_title,Chưa có dữ liệu lịch sử!,暫無歷史數據！
label:wujia.franchise.inspection:chart_no_data_desc,Vui lòng chọn Mẫu khảo sát hoặc cửa hàng này chưa có phiếu giám sát nào theo mẫu này ở trạng thái Hoàn thành / Cần khắc phục.,請選擇評核範本，或此門店目前尚無此範本已完成／待改善之監督表記錄。"""

if "chart_history_title" not in csv_text:
    csv_text += chart_entries + "\n"

with open(csv_path, "w", encoding="utf-8") as f:
    f.write(csv_text)

# 2. Update JS
js_path = "/home/dev/WujiaTea-ERP-internal/custom/wujia_franchise/static/src/js/wujia_inspection_chart.js"
with open(js_path, "r", encoding="utf-8") as f:
    js_text = f.read()

js_text = js_text.replace(
    'return _t("Lịch sử điểm số giám sát (10 đợt gần nhất)");',
    'return _t("label:wujia.franchise.inspection:chart_history_title");'
)
js_text = js_text.replace(
    'return _t("Điểm từng đợt");',
    'return _t("label:wujia.franchise.inspection:chart_single_score");'
)
js_text = js_text.replace(
    'return _t("Điểm trung bình");',
    'return _t("label:wujia.franchise.inspection:chart_avg_score");'
)
js_text = js_text.replace(
    'return _t("Chưa có dữ liệu lịch sử!");',
    'return _t("label:wujia.franchise.inspection:chart_no_data_title");'
)
js_text = js_text.replace(
    'return _t("Vui lòng chọn Mẫu khảo sát hoặc cửa hàng này chưa có phiếu giám sát nào theo mẫu này ở trạng thái Hoàn thành / Cần khắc phục.");',
    'return _t("label:wujia.franchise.inspection:chart_no_data_desc");'
)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_text)

print("Updated CSV and JS with translation keys successfully!")
