/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class InspectionScheduleCustom extends Component {
    static template = "wujia_franchise.InspectionScheduleCustom";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        
        const today = new Date().toISOString().split('T')[0];

        this.state = useState({
            selectedDate: today,
            selectedInspectorId: 0,
            searchQuery: "",
            statusFilter: "all",
            areaFilter: "all",
            franchises: [],
            inspectors: [],
            areas: [],
            inspections: [],
            statuses: {},
            checkedFranchises: {},
            upcomingInspections: [],
        });

        onWillStart(async () => {
            try {
                await this.loadFullCalendar();
            } catch (err) {
                console.error("Lỗi khi tải FullCalendar từ CDN:", err);
            }
            await this.loadData();
        });

        onMounted(() => {
            this.renderCalendar();
        });
    }

    async loadFullCalendar() {
        if (window.FullCalendar) {
            return;
        }
        return new Promise((resolve, reject) => {
            const script = document.createElement("script");
            script.src = "https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.js";
            script.onload = () => resolve();
            script.onerror = () => reject(new Error("Failed to load FullCalendar from CDN"));
            document.head.appendChild(script);
        });
    }

    async loadData() {
        const data = await this.orm.call(
            "wujia.franchise.inspection",
            "get_schedule_data",
            [],
            {}
        );

        this.state.franchises = data.franchises || [];
        this.state.inspectors = data.inspectors || [];
        this.state.areas = data.areas || [];
        this.state.inspections = data.inspections || [];
        this.state.statuses = data.statuses || {};

        this.updateCheckedFranchises();
        if (this.calendar) {
            this.calendar.refetchEvents();
        }
    }

    updateCheckedFranchises() {
        const dateStr = this.state.selectedDate;
        const currentInspections = this.state.inspections.filter(
            i => i.planned_date && i.planned_date.substring(0, 10) === dateStr
        );

        const checks = {};
        this.state.franchises.forEach(f => {
            checks[f.id] = false;
        });

        currentInspections.forEach(i => {
            checks[i.franchise_id] = true;
        });

        this.state.checkedFranchises = checks;

        if (currentInspections.length > 0 && currentInspections[0].inspector_id) {
            this.state.selectedInspectorId = currentInspections[0].inspector_id;
        } else {
            this.state.selectedInspectorId = 0;
        }

        const todayStr = new Date().toISOString().split('T')[0];
        const upcoming = this.state.inspections
            .filter(i => i.planned_date && i.planned_date.substring(0, 10) >= todayStr)
            .sort((a, b) => a.planned_date.localeCompare(b.planned_date));
        this.state.upcomingInspections = upcoming;
    }

    renderCalendar() {
        const container = document.getElementById("calendar_container");
        if (!container) return;

        if (this.calendar) {
            this.calendar.destroy();
        }

        const self = this;
        const fc = window.FullCalendar;
        if (!fc) {
            console.error("FullCalendar library is not loaded.");
            return;
        }

        this.calendar = new fc.Calendar(container, {
            initialView: 'dayGridMonth',
            initialDate: this.state.selectedDate,
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: ''
            },
            events: function(info, successCallback, failureCallback) {
                const events = self.state.inspections.map(i => {
                    let color = '#17a2b8';
                    if (i.state === 'in_progress') color = '#ffc107';
                    if (i.state === 'submitted') color = '#28a745';
                    if (i.state === 'approved') color = '#007bff';
                    
                    return {
                        id: i.id,
                        title: i.franchise_code ? '[' + i.franchise_code + '] ' + i.franchise_name : i.franchise_name,
                        start: i.planned_date.substring(0, 10),
                        backgroundColor: color,
                        borderColor: color,
                        allDay: true,
                    };
                });
                successCallback(events);
            },
            dateClick: function(info) {
                self.state.selectedDate = info.dateStr;
                self.updateCheckedFranchises();
                
                document.querySelectorAll('.fc-day').forEach(el => {
                    el.style.backgroundColor = '';
                });
                info.dayEl.style.backgroundColor = '#eef3f7';
            },
             datesSet: function(dateInfo) {
                const midDate = new Date((dateInfo.start.getTime() + dateInfo.end.getTime()) / 2);
                const midDateStr = midDate.toISOString().split('T')[0];
                
                const currentMonth = self.state.selectedDate.substring(0, 7);
                const newMonth = midDateStr.substring(0, 7);
                
                if (currentMonth !== newMonth) {
                    self.state.selectedDate = midDateStr;
                    self.updateCheckedFranchises();
                }
            }
        });

        this.calendar.render();
    }

    get filteredFranchises() {
        return this.state.franchises.filter(f => {
            const matchesSearch = f.name.toLowerCase().includes(this.state.searchQuery.toLowerCase()) || 
                                  f.code.toLowerCase().includes(this.state.searchQuery.toLowerCase());
            
            const matchesStatus = this.state.statusFilter === 'all' || 
                                  (this.state.statusFilter === 'checked' && this.state.checkedFranchises[f.id]) ||
                                  (this.state.statusFilter === 'unchecked' && !this.state.checkedFranchises[f.id]) ||
                                  f.status === this.state.statusFilter;

            const matchesArea = this.state.areaFilter === 'all' || 
                                f.area_id === parseInt(this.state.areaFilter);

            return matchesSearch && matchesStatus && matchesArea;
        });
    }

    onCheckFranchise(ev, fid) {
        this.state.checkedFranchises[fid] = ev.target.checked;
    }

    async onSave() {
        const checkedIds = [];
        Object.keys(this.state.checkedFranchises).forEach(fid => {
            if (this.state.checkedFranchises[fid]) {
                checkedIds.push(parseInt(fid));
            }
        });

        try {
            await this.orm.call(
                "wujia.franchise.inspection",
                "save_schedule_data",
                [],
                {
                    date_str: this.state.selectedDate,
                    inspector_id: parseInt(this.state.selectedInspectorId) || false,
                    franchise_ids: checkedIds
                }
            );
            this.notification.add("Lưu lịch giám sát thành công!", { type: "success" });
            await this.loadData();
            this.renderCalendar();
        } catch (error) {
            this.notification.add("Đã xảy ra lỗi khi lưu lịch giám sát.", { type: "danger" });
        }
    }
}

registry.category("actions").add("wujia_franchise.inspection_schedule_custom", InspectionScheduleCustom);
