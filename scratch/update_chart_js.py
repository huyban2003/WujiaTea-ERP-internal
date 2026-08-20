js_path = "/home/dev/WujiaTea-ERP-internal/custom/wujia_franchise/static/src/js/wujia_inspection_chart.js"
with open(js_path, "r", encoding="utf-8") as f:
    code = f.read()

old_block = """    get chartTitle() {
        return _t("label:wujia.franchise.inspection:chart_history_title");
    }

    get singleScoreLabel() {
        return _t("label:wujia.franchise.inspection:chart_single_score");
    }

    get avgScoreLabel() {
        return _t("label:wujia.franchise.inspection:chart_avg_score");
    }

    get noDataTitle() {
        return _t("label:wujia.franchise.inspection:chart_no_data_title");
    }

    get noDataDesc() {
        return _t("label:wujia.franchise.inspection:chart_no_data_desc");
    }"""

new_block = """    get chartTitle() {
        return this.chartData.title || _t("label:wujia.franchise.inspection:chart_history_title");
    }

    get singleScoreLabel() {
        return this.chartData.single_label || _t("label:wujia.franchise.inspection:chart_single_score");
    }

    get avgScoreLabel() {
        return this.chartData.avg_label || _t("label:wujia.franchise.inspection:chart_avg_score");
    }

    get noDataTitle() {
        return this.chartData.no_data_title || _t("label:wujia.franchise.inspection:chart_no_data_title");
    }

    get noDataDesc() {
        return this.chartData.no_data_desc || _t("label:wujia.franchise.inspection:chart_no_data_desc");
    }"""

code = code.replace(old_block, new_block)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated JS successfully!")
