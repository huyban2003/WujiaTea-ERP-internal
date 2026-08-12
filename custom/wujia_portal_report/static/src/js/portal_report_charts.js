/* Báo cáo — chart bằng ApexCharts (đã load sẵn ở wujia_portal_layout/assets).
 *
 * Quy ước BA (STT12 #4): chiều cao cột = DOANH THU, số in trên/trong cột = SỐ ĐƠN.
 * Vì vậy chỉ còn 1 series cột; số đơn đi vào dataLabels chứ không thành series thứ 2
 * (series đường cũ làm hai đơn vị đo chung một khung, đọc sai tỷ lệ tiền).
 *
 * Payload JSON đọc từ data-chart-payload → 1 init/chart, KHÔNG thêm AJAX.
 * Chart nằm trong vùng swap của wj_ajax_list → vẽ lại sau mỗi lần lọc, nếu không
 * ApexCharts đã render vào node cũ (đã bị thay) và biểu đồ biến mất.
 */
(function () {
    "use strict";

    var charts = [];

    function wujiaColor(name, fallback) {
        var v = getComputedStyle(document.documentElement)
            .getPropertyValue("--wujia-" + name).trim();
        return v || fallback;
    }

    /* 2.800.000 → "2,8tr" · 700.000 → "700k". Mockup dùng đúng 2 mốc này. */
    function shortMoney(v) {
        var n = Number(v) || 0;
        if (Math.abs(n) >= 1e6) {
            return String(Math.round(n / 1e5) / 10).replace(".", ",") + "tr";
        }
        if (Math.abs(n) >= 1e3) {
            return Math.round(n / 1e3) + "k";
        }
        return String(Math.round(n));
    }

    function fullMoney(v) {
        return Number(v || 0).toLocaleString("vi-VN");
    }

    function monthsOptions(payload, mobile) {
        var primary = wujiaColor("primary", "#28A9DF");
        /* yaxis.title chỉ được TỒN TẠI ở bản PC. Truyền title: undefined làm
           ApexCharts đọc title.text của undefined → ném lỗi và chart mobile
           không vẽ ra gì (canvas rỗng), nên phải bỏ hẳn khoá. */
        var yaxis = {
            labels: {
                formatter: shortMoney,
                style: { fontSize: mobile ? "11px" : "12px" },
            },
        };
        if (!mobile) {
            /* Ký hiệu tiền lấy từ payload (currency công ty), không gõ 'đ' cứng. */
            yaxis.title = {
                text: "Doanh thu" + (payload.currency ? " (" + payload.currency + ")" : ""),
                style: { fontWeight: 500 },
            };
        }
        return {
            chart: {
                type: "bar",
                height: mobile ? 180 : 250,
                toolbar: { show: false },
                fontFamily: "inherit",
                parentHeightOffset: 0,
            },
            series: [{ name: "Doanh thu", data: payload.months_total || [] }],
            colors: [primary],
            plotOptions: {
                bar: {
                    columnWidth: mobile ? "45%" : "38%",
                    borderRadius: 4,
                    /* Mockup đặt số đơn NẰM TRONG cột, sát mép trên (cách ~9px). */
                    dataLabels: { position: "top" },
                },
            },
            /* Nhãn = SỐ ĐƠN. Cột thấp thì Apex tự đẩy nhãn ra ngoài đỉnh cột
               (dataLabels.position + offset), tỷ lệ tiền của cột không đổi. */
            dataLabels: {
                enabled: true,
                formatter: function (val, opt) {
                    var counts = payload.months_count || [];
                    return counts[opt.dataPointIndex] != null
                        ? String(counts[opt.dataPointIndex]) : "";
                },
                offsetY: 16,
                /* Mockup vẽ chữ trắng trong cột, nhưng cột thấp (tháng ít doanh thu)
                   đẩy nhãn ra nền trắng → mất chữ. Bản ApexCharts đang bundle cũng
                   KHÔNG nhận hàm cho style.colors (ném lỗi, chart không vẽ), nên
                   dùng một màu tối duy nhất: đọc được cả trong cột lẫn trên nền. */
                style: {
                    fontSize: "12px",
                    fontWeight: 700,
                    colors: [wujiaColor("text-primary", "#111827")],
                },
            },
            xaxis: {
                categories: payload.months_label || [],
                axisBorder: { show: false },
                axisTicks: { show: false },
                labels: {
                    rotate: 0,
                    hideOverlappingLabels: true,
                    style: { fontSize: mobile ? "11px" : "12px" },
                },
            },
            yaxis: yaxis,
            grid: { borderColor: wujiaColor("border-soft", "#EEF2F5"), strokeDashArray: 0 },
            legend: { show: false },
            tooltip: {
                y: {
                    formatter: function (v, opt) {
                        var counts = payload.months_count || [];
                        var c = counts[opt.dataPointIndex];
                        return fullMoney(v) + (c != null ? " · " + c + " đơn" : "");
                    },
                },
            },
        };
    }

    function stateOptions(payload) {
        return {
            chart: { type: "donut", height: 200, fontFamily: "inherit" },
            series: payload.state_count || [],
            labels: payload.state_label || [],
            colors: payload.state_color || [],
            legend: { show: false },
            dataLabels: { enabled: false },
            stroke: { width: 0 },
            plotOptions: {
                pie: {
                    donut: {
                        size: "70%",
                        labels: {
                            show: true,
                            value: { fontSize: "26px", fontWeight: 700, offsetY: 2 },
                            total: {
                                show: true,
                                label: "Tổng",
                                fontSize: "13px",
                                formatter: function (w) {
                                    return w.globals.seriesTotals.reduce(function (a, b) {
                                        return a + b;
                                    }, 0);
                                },
                            },
                        },
                    },
                },
            },
            tooltip: { y: { formatter: function (v) { return v + " đơn"; } } },
        };
    }

    function readPayload(node) {
        try {
            return JSON.parse(node.dataset.chartPayload || "{}");
        } catch (e) {
            console.warn("[portal_report] Cannot parse chart payload", e);
            return null;
        }
    }

    function renderInto(node, options) {
        var chart = new ApexCharts(node, options);
        charts.push(chart);
        chart.render();
    }

    function emptyNote(node) {
        node.innerHTML = '<p class="wj-rep-chart-empty">Chưa có dữ liệu trong khoảng đã chọn.</p>';
    }

    function render() {
        while (charts.length) {
            charts.pop().destroy();
        }
        if (typeof ApexCharts === "undefined") {
            return;
        }

        /* Cả 2 bố cục cùng trong DOM (một cái display:none) — chỉ vẽ cái đang hiện,
           Apex đo sai kích thước khi container bị ẩn. */
        [
            { id: "report-chart-months", mobile: false },
            { id: "report-chart-months-m", mobile: true },
        ].forEach(function (spec) {
            var node = document.getElementById(spec.id);
            if (!node || !node.offsetParent) {
                return;
            }
            var payload = readPayload(node);
            if (!payload) {
                return;
            }
            if (payload.months_label && payload.months_label.length) {
                renderInto(node, monthsOptions(payload, spec.mobile));
            } else {
                emptyNote(node);
            }
        });

        var stateNode = document.getElementById("report-chart-state");
        if (stateNode && stateNode.offsetParent) {
            var pcNode = document.getElementById("report-chart-months");
            var payload = pcNode ? readPayload(pcNode) : null;
            if (payload && payload.state_label && payload.state_label.length) {
                renderInto(stateNode, stateOptions(payload));
            } else {
                emptyNote(stateNode);
            }
        }
    }

    document.addEventListener("DOMContentLoaded", render);
    document.addEventListener("wj:list:swapped", render);
    /* Đổi bề rộng qua mốc 992 → bố cục kia lên sóng, chart của nó chưa từng vẽ. */
    window.addEventListener("resize", function () {
        clearTimeout(render._t);
        render._t = setTimeout(render, 200);
    });
})();
