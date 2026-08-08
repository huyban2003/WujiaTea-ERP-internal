/* Báo cáo — render chart bằng ApexCharts (đã load sẵn ở wujia_portal_layout/assets).
   Đọc payload JSON từ data-chart-payload attribute → 1 init / chart, KHÔNG thêm AJAX. */
(function () {
    "use strict";
    function wujiaColor(name, fallback) {
        const v = getComputedStyle(document.documentElement)
            .getPropertyValue("--wujia-" + name).trim();
        return v || fallback;
    }

    // Chart nằm TRONG vùng swap của wj_ajax_list → vẽ lại sau mỗi lần lọc, nếu không
    // ApexCharts đã render vào node cũ (đã bị thay) và biểu đồ biến mất.
    const charts = [];

    function render() {
        while (charts.length) {
            charts.pop().destroy();
        }
        const wrap = document.getElementById("report-chart-months");
        if (!wrap || typeof ApexCharts === "undefined") return;

        let payload;
        try {
            payload = JSON.parse(wrap.dataset.chartPayload || "{}");
        } catch (e) {
            console.warn("[portal_report] Cannot parse chart payload", e);
            return;
        }

        const colorPrimary = wujiaColor("primary", "#28A9DF");
        const colorSuccess = wujiaColor("success", "#16A34A");

        // ---- Chart 1: Bar — đơn hàng theo tháng ----
        if (payload.months_label && payload.months_label.length) {
            const optionsMonths = {
                chart: { type: "bar", height: 280, toolbar: { show: false }, fontFamily: "inherit" },
                series: [
                    { name: "Số đơn", data: payload.months_count || [], type: "column" },
                    { name: "Doanh thu (₫)", data: payload.months_total || [], type: "line" },
                ],
                stroke: { width: [0, 3], curve: "smooth" },
                colors: [colorPrimary, colorSuccess],
                plotOptions: { bar: { columnWidth: "50%", borderRadius: 4 } },
                xaxis: { categories: payload.months_label },
                yaxis: [
                    { title: { text: "Số đơn" }, decimalsInFloat: 0 },
                    { opposite: true, title: { text: "Doanh thu (₫)" },
                      labels: { formatter: function (v) { return Number(v).toLocaleString("vi-VN"); } } },
                ],
                tooltip: {
                    shared: true, intersect: false,
                    y: [
                        { formatter: function (v) { return Math.round(v) + " đơn"; } },
                        { formatter: function (v) { return Number(v).toLocaleString("vi-VN") + " ₫"; } },
                    ],
                },
                legend: { position: "top", horizontalAlign: "right" },
            };
            const chartMonths = new ApexCharts(wrap, optionsMonths);
            charts.push(chartMonths);
            chartMonths.render();
        } else {
            wrap.innerHTML = '<div class="alert alert-info mb-0">Chưa có dữ liệu trong khoảng đã chọn.</div>';
        }

        // ---- Chart 2: Donut — phân bố trạng thái ----
        const stateWrap = document.getElementById("report-chart-state");
        if (stateWrap && payload.state_label && payload.state_label.length) {
            const optionsState = {
                chart: { type: "donut", height: 240, fontFamily: "inherit" },
                series: payload.state_count || [],
                labels: payload.state_label || [],
                colors: payload.state_color || [],
                legend: { show: false },
                dataLabels: {
                    enabled: true,
                    formatter: function (val) { return val.toFixed(1) + "%"; },
                },
                plotOptions: {
                    pie: { donut: { size: "65%", labels: {
                        show: true,
                        total: { show: true, label: "Tổng", formatter: function (w) {
                            return w.globals.seriesTotals.reduce((a, b) => a + b, 0);
                        } },
                    } } },
                },
            };
            const chartState = new ApexCharts(stateWrap, optionsState);
            charts.push(chartState);
            chartState.render();
        } else if (stateWrap) {
            stateWrap.innerHTML = '<div class="text-muted text-center py-4">Chưa có dữ liệu.</div>';
        }
    }

    document.addEventListener("DOMContentLoaded", render);
    document.addEventListener("wj:list:swapped", render);
})();
