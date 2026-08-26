/**
 * JavaScript Controller for Wujia Franchise Inspection Standalone Web Survey
 */

(function () {
  "use strict";
  function _t(key, defVal) {
    return (window.SURVEY_TRANS && window.SURVEY_TRANS[key]) || defVal || key;
  }

  document.addEventListener("DOMContentLoaded", function () {
    const app = document.getElementById("surveyApp");
    if (!app) return;

    // Auto trim leading/trailing whitespace caused by IDE XML auto-formatters
    function cleanExamTextareas() {
      document.querySelectorAll(".exam-ans").forEach(function (el) {
        if (el.value) {
          el.value = el.value.trim();
        }
      });
    }

    cleanExamTextareas();

    // Clean when focus or input on textareas
    document.querySelectorAll(".exam-ans").forEach(function (el) {
      el.addEventListener("focus", function () {
        if (this.value) this.value = this.value.trim();
      });
    });

    const inspectionId = parseInt(app.dataset.inspectionId);
    const maxScore = parseFloat(app.dataset.maxChecklistScore || "95");
    let isExamSubmitted = app.dataset.isExamSubmitted === "true";
    let isInspectionClosed = app.dataset.isInspectionClosed === "true";

    function lockExamTab() {
      isExamSubmitted = true;
      app.dataset.isExamSubmitted = "true";

      const nameInput = document.getElementById("testEmployeeName");
      if (nameInput) {
        nameInput.readOnly = true;
        nameInput.style.backgroundColor = "#f8fafc";
      }
      const tenureInput = document.getElementById("tenure");
      if (tenureInput) {
        tenureInput.readOnly = true;
        tenureInput.style.backgroundColor = "#f8fafc";
      }
      document.querySelectorAll(".exam-ans").forEach(function (textarea) {
        textarea.readOnly = true;
        textarea.style.backgroundColor = "#f8fafc";
      });

      const lockBadge = document.getElementById("examLockStatusBadge");
      if (lockBadge) {
        lockBadge.style.display = "inline-flex";
      }
    }

    function lockEntireInspection() {
      isInspectionClosed = true;
      lockExamTab();

      document.querySelectorAll(".line-check").forEach(function (chk) {
        chk.disabled = true;
      });
      document.querySelectorAll(".line-note").forEach(function (input) {
        input.readOnly = true;
        input.style.backgroundColor = "#f8fafc";
      });
      document.querySelectorAll(".btn-trigger-upload").forEach(function (btn) {
        btn.style.display = "none";
      });
      document.querySelectorAll(".line-file").forEach(function (input) {
        input.disabled = true;
      });

      const submitBtn = document.getElementById("btnFinishSurvey");
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML =
          '<i class="fa fa-lock"></i> ' +
          _t(
            "label:wujia.franchise.inspection_survey:status_completed",
            "Completed &amp; Locked",
          );
        submitBtn.style.background = "#64748b";
        submitBtn.style.boxShadow = "none";
        submitBtn.style.cursor = "not-allowed";
      }
    }

    if (isInspectionClosed) {
      lockEntireInspection();
    } else if (isExamSubmitted) {
      lockExamTab();
    }

    // Tab Switching
    const tabChecklistBtn = document.getElementById("tabChecklistBtn");
    const tabExamBtn = document.getElementById("tabExamBtn");
    const tabNotesBtn = document.getElementById("tabNotesBtn");
    const tabConfirmationBtn = document.getElementById("tabConfirmationBtn");
    const tabChecklistContent = document.getElementById("tabChecklistContent");
    const tabExamContent = document.getElementById("tabExamContent");
    const tabNotesContent = document.getElementById("tabNotesContent");
    const tabConfirmationContent = document.getElementById(
      "tabConfirmationContent",
    );

    function switchTab(tab) {
      sessionStorage.setItem("wujia_survey_active_tab_" + inspectionId, tab);
      if (tabChecklistContent)
        tabChecklistContent.style.display =
          tab === "checklist" ? "block" : "none";
      if (tabExamContent)
        tabExamContent.style.display = tab === "exam" ? "block" : "none";
      if (tabNotesContent)
        tabNotesContent.style.display = tab === "notes" ? "block" : "none";
      if (tabRevenueContent)
        tabRevenueContent.style.display = tab === "revenue" ? "block" : "none";
      if (tabConfirmationContent)
        tabConfirmationContent.style.display =
          tab === "confirmation" ? "block" : "none";
      if (tabChecklistBtn)
        tabChecklistBtn.classList.toggle("active", tab === "checklist");
      if (tabExamBtn) tabExamBtn.classList.toggle("active", tab === "exam");
      if (tabNotesBtn) tabNotesBtn.classList.toggle("active", tab === "notes");
      if (tabRevenueBtn)
        tabRevenueBtn.classList.toggle("active", tab === "revenue");
      if (tabConfirmationBtn)
        tabConfirmationBtn.classList.toggle("active", tab === "confirmation");
      if (tab === "confirmation") {
        setTimeout(function () {
          if (typeof resizeCanvas === "function") resizeCanvas();
        }, 60);
      }
    }

    const savedTab = sessionStorage.getItem(
      "wujia_survey_active_tab_" + inspectionId,
    );
    const hash = window.location.hash;
    if (hash && hash.includes("tab=confirmation")) {
      switchTab("confirmation");
    } else if (hash && hash.includes("tab=revenue")) {
      switchTab("revenue");
    } else if (hash && hash.includes("tab=notes")) {
      switchTab("notes");
    } else if (hash && hash.includes("tab=exam")) {
      switchTab("exam");
    } else if (
      savedTab &&
      ["checklist", "exam", "notes", "revenue", "confirmation"].includes(savedTab)
    ) {
      switchTab(savedTab);
    }

    if (tabChecklistBtn) {
      tabChecklistBtn.addEventListener("click", function () {
        switchTab("checklist");
      });
    }
    if (tabExamBtn) {
      tabExamBtn.addEventListener("click", function () {
        switchTab("exam");
      });
    }
    if (tabNotesBtn) {
      tabNotesBtn.addEventListener("click", function () {
        switchTab("notes");
      });
    }
    if (tabRevenueBtn) {
      tabRevenueBtn.addEventListener("click", function () {
        switchTab("revenue");
      });
    }
    if (tabConfirmationBtn) {
      tabConfirmationBtn.addEventListener("click", function () {
        switchTab("confirmation");
      });
    }

    // Attendance present counter
    function updatePresentCount() {
      let count = 0;
      document.querySelectorAll(".att-present-check").forEach(function (chk) {
        if (chk.checked) count++;
      });
      const el = document.getElementById("livePresentCount");
      if (el) el.innerText = count;
    }
    document.querySelectorAll(".att-present-check").forEach(function (chk) {
      chk.addEventListener("change", updatePresentCount);
    });

    // Toast notifications
    function showToast(msg, isError) {
      const t = document.getElementById("toast");
      if (!t) return;
      t.innerText = msg;
      t.style.background = isError ? "#ef4444" : "#3b82f6";
      t.style.display = "block";
      setTimeout(function () {
        t.style.display = "none";
      }, 3500);
    }

    // Custom Alert Modal
    const customAlertModalOverlay = document.getElementById(
      "customAlertModalOverlay",
    );
    const customAlertMessage = document.getElementById("customAlertMessage");
    const customAlertClose = document.getElementById("customAlertClose");
    const customAlertBtnOk = document.getElementById("customAlertBtnOk");
    let alertCallback = null;

    function showCustomAlert(msg, callback) {
      if (customAlertMessage) customAlertMessage.innerText = msg;
      alertCallback = callback || null;
      if (customAlertModalOverlay)
        customAlertModalOverlay.style.display = "flex";
    }

    function hideCustomAlert() {
      if (customAlertModalOverlay)
        customAlertModalOverlay.style.display = "none";
      if (alertCallback) {
        const cb = alertCallback;
        alertCallback = null;
        cb();
      }
    }

    if (customAlertClose)
      customAlertClose.addEventListener("click", hideCustomAlert);
    if (customAlertBtnOk)
      customAlertBtnOk.addEventListener("click", hideCustomAlert);
    if (customAlertModalOverlay) {
      customAlertModalOverlay.addEventListener("click", function (e) {
        if (e.target === customAlertModalOverlay) hideCustomAlert();
      });
    }

    function openPrevModal(data) {
      // Prev modal removed
    }

    // Click "Đợt trước" badge handler
    document.querySelectorAll(".btn-prev-info").forEach(function (btn) {
      btn.addEventListener("click", function () {
        const rawJson = this.dataset.prevInfo;
        if (rawJson && rawJson !== "null") {
          try {
            const data = JSON.parse(rawJson);
            openPrevModal(data);
          } catch (err) {
            alert(
              _t(
                "label:wujia.franchise.inspection_survey:no_prev_data",
                "No previous inspection data available for this criterion.",
              ),
            );
          }
        } else {
          alert(
            _t(
              "label:wujia.franchise.inspection_survey:no_prev_data",
              "No previous inspection data available for this criterion.",
            ),
          );
        }
      });
    });

    // Real-time Checklist Live Score, Total Score & Grade calculation
    const surveyGrades = window.SURVEY_GRADES || [];

    function updateLiveScore() {
      let deductions = 0;
      document.querySelectorAll(".item-row").forEach(function (row) {
        const chk = row.querySelector(".line-check");
        if (chk && !chk.checked) {
          deductions += parseFloat(row.dataset.deduction || "0");
        }
      });
      const currentChecklistScore = Math.max(0, maxScore - deductions);

      // 1. Update Checklist Score
      const liveChecklistScoreEl =
        document.getElementById("liveChecklistScore");
      if (liveChecklistScoreEl) {
        const formattedChecklist = Number.isInteger(currentChecklistScore)
          ? currentChecklistScore
          : currentChecklistScore.toFixed(1);
        liveChecklistScoreEl.innerText = formattedChecklist + " / " + maxScore;
      }

      // 2. Read Exam Score
      const appEl = document.getElementById("surveyApp");
      const examScore = parseFloat(
        appEl ? appEl.dataset.examScore || "0" : "0",
      );
      const currentTotalScore = currentChecklistScore + examScore;

      // 3. Update Total Score
      const liveTotalScoreEl = document.getElementById("liveTotalScore");
      if (liveTotalScoreEl) {
        liveTotalScoreEl.innerText = Number.isInteger(currentTotalScore)
          ? currentTotalScore
          : currentTotalScore.toFixed(1);
      }

      // 4. Update Grade (Xếp loại A, B, C, D...)
      const liveGradeEl = document.getElementById("liveGrade");
      if (liveGradeEl) {
        let matchedGrade = "---";
        for (let i = 0; i < surveyGrades.length; i++) {
          const g = surveyGrades[i];
          if (
            currentTotalScore >= g.min_score &&
            currentTotalScore <= g.max_score
          ) {
            matchedGrade = g.name;
            break;
          }
        }
        liveGradeEl.innerText = matchedGrade;
      }

      // 5. Update each Section's Earned / Total score badge in real time
      document.querySelectorAll(".section-row").forEach(function (secRow) {
        const secId = secRow.dataset.sectionId;
        if (!secId) return;
        let secTotal = 0;
        let secEarned = 0;
        const secItems = document.querySelectorAll(
          '.item-row[data-section-id="' + secId + '"]',
        );
        secItems.forEach(function (item) {
          const deduction = parseFloat(item.dataset.deduction || "0");
          secTotal += deduction;
          const chk = item.querySelector(".line-check");
          if (chk && chk.checked) {
            secEarned += deduction;
          }
        });
        const earnedEl = secRow.querySelector(".sec-earned");
        const totalEl = secRow.querySelector(".sec-total");
        const badgeEl = secRow.querySelector(".section-score-badge");
        if (earnedEl) {
          earnedEl.innerText = Number.isInteger(secEarned)
            ? secEarned
            : secEarned.toFixed(1);
        }
        if (totalEl) {
          totalEl.innerText = Number.isInteger(secTotal)
            ? secTotal
            : secTotal.toFixed(1);
        }
        if (badgeEl) {
          if (secEarned === secTotal && secTotal > 0) {
            badgeEl.style.background = "#dcfce7";
            badgeEl.style.color = "#15803d";
            badgeEl.style.borderColor = "#86efac";
          } else {
            badgeEl.style.background = "#ffffff";
            badgeEl.style.color = "#1e293b";
            badgeEl.style.borderColor = "#cbd5e1";
          }
        }
      });
    }

    document.querySelectorAll(".line-check").forEach(function (chk) {
      chk.addEventListener("change", updateLiveScore);
    });

    // Run initial calculation
    updateLiveScore();

    // Image file upload preview
    document.querySelectorAll(".item-row").forEach(function (row) {
      const fileInput = row.querySelector(".line-file");
      const triggerBtn = row.querySelector(".btn-trigger-upload");
      const previewImg = row.querySelector(".img-preview");

      if (triggerBtn && fileInput) {
        triggerBtn.addEventListener("click", function () {
          if (!isInspectionClosed) fileInput.click();
        });
      }
      if (previewImg && fileInput) {
        previewImg.addEventListener("click", function () {
          if (!isInspectionClosed) fileInput.click();
        });
      }

      if (fileInput) {
        fileInput.addEventListener("change", function () {
          if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
              if (previewImg) {
                previewImg.src = e.target.result;
                previewImg.style.display = "block";
              }
              if (triggerBtn) {
                triggerBtn.style.display = "none";
              }
              row.dataset.b64Image = e.target.result;
              const photoInd = row.querySelector(".photo-indicator");
              if (photoInd) photoInd.style.display = "inline-flex";
            };
            reader.readAsDataURL(this.files[0]);
          }
        });
      }
    });

    // Save survey data via AJAX (only lock exam tab on save)
    async function saveDataAndEvaluate() {
      if (isInspectionClosed) return;

      const nameInput = document.getElementById("testEmployeeName");
      const tenureInput = document.getElementById("tenure");

      const empName = nameInput ? nameInput.value.trim() : "";
      const empTenure = tenureInput ? tenureInput.value.trim() : "";

      // MUST REQUIRE Nhân viên được kiểm tra (test_employee_name)
      if (!isExamSubmitted && !empName) {
        showCustomAlert(
          _t(
            "label:wujia.franchise.inspection_survey:alert_msg_input_employee",
            "Please enter Tested Employee name before saving!",
          ),
          function () {
            switchTab("exam");
            if (nameInput) {
              nameInput.scrollIntoView({ behavior: "smooth", block: "center" });
              nameInput.focus();
              nameInput.style.borderColor = "#ef4444";
              nameInput.style.boxShadow = "0 0 0 3px rgba(239, 68, 68, 0.3)";
            }
          },
        );
        return false;
      } else if (nameInput) {
        nameInput.style.borderColor = "#cbd5e1";
        nameInput.style.boxShadow = "none";
      }

      const lines = [];
      document.querySelectorAll(".item-row").forEach(function (row) {
        const id = row.dataset.id;
        const chk = row.querySelector(".line-check");
        const noteInput = row.querySelector(".line-note");
        const isPass = chk ? chk.checked : true;
        const note = noteInput ? noteInput.value : "";
        const b64 = row.dataset.b64Image || null;

        const item = { id: parseInt(id), is_pass: isPass, note: note };
        if (b64) item.evidence_image = b64;
        lines.push(item);
      });

      const examLines = [];
      document.querySelectorAll(".exam-row").forEach(function (row) {
        const id = row.dataset.id;
        const ansInput = row.querySelector(".exam-ans");
        const ans = ansInput ? ansInput.value : "";
        examLines.push({ id: parseInt(id), answer: ans });
      });

      const attendanceLines = [];
      document.querySelectorAll(".attendance-row").forEach(function (row) {
        const id = row.dataset.id;
        const nameInput = row.querySelector(".att-name-input");
        const roleSelect = row.querySelector(".att-role-select");
        const phoneInput = row.querySelector(".att-phone-input");
        const isPresentChk = row.querySelector(".att-present-check");
        const noteInput = row.querySelector(".att-note-input");

        const isPresent = isPresentChk ? isPresentChk.checked : true;
        const note = noteInput ? noteInput.value : "";
        const name = nameInput ? nameInput.value : "";
        const role = roleSelect ? roleSelect.value : "staff";
        const phone = phoneInput ? phoneInput.value : "";

        attendanceLines.push({
          id: parseInt(id),
          employee_name: name,
          role: role,
          phone: phone,
          is_present: isPresent,
          note: note,
        });
      });

      const confirmedMemberSelect = document.getElementById(
        "confirmedMemberSelect",
      );
      const confirmedMemberId = confirmedMemberSelect
        ? confirmedMemberSelect.value || false
        : false;

      const saveLoadingOverlay = document.getElementById("saveLoadingOverlay");
      const btnFinishSurvey = document.getElementById("btnFinishSurvey");
      let origSaveBtnHtml = "";

      if (saveLoadingOverlay) {
        saveLoadingOverlay.style.display = "flex";
      }
      if (btnFinishSurvey) {
        origSaveBtnHtml = btnFinishSurvey.innerHTML;
        btnFinishSurvey.disabled = true;
        btnFinishSurvey.style.pointerEvents = "none";
        btnFinishSurvey.style.opacity = "0.75";
        btnFinishSurvey.innerHTML = `<i class="fa fa-spinner fa-spin me-2"></i> ${_t("label:wujia.franchise.inspection_survey:label_saving", "Đang lưu...")}`;
      }

      try {
        const res = await fetch(
          "/franchise/inspection/do/" + inspectionId + "/save",
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              jsonrpc: "2.0",
              method: "call",
              params: {
                inspection_id: inspectionId,
                lines: lines,
                exam_lines: examLines,
                test_employee_name: empName,
                tenure: empTenure,
                store_appearance_issues: document.getElementById(
                  "storeAppearanceIssues",
                )
                  ? document.getElementById("storeAppearanceIssues").value
                  : "",
                confirmed_member_id: confirmedMemberId,
                attendance_lines: attendanceLines,
                signature_image: document.getElementById("signatureDataInput")
                  ? document.getElementById("signatureDataInput").value
                  : "",
                report_lines: (function () {
                  const revList = [];
                  const rows = document.querySelectorAll(
                    "#revenueTbody .revenue-row",
                  );
                  rows.forEach((r) => {
                    const id = r.dataset.id ? parseInt(r.dataset.id) : null;
                    const mSel = r.querySelector(".rev-month-sel");
                    const ySel = r.querySelector(".rev-year-sel");
                    const revInp = r.querySelector(".rev-amount-input");
                    const avgInp = r.querySelector(".rev-avg-input");
                    const appInp = r.querySelector(".rev-app-sale-input");
                    const pctInp = r.querySelector(".rev-percent-input");
                    const mVal = mSel ? mSel.value : "01";
                    const yVal = ySel ? ySel.value : "2026";
                    revList.push({
                      id: id,
                      date_month: `${yVal}-${mVal}-01`,
                      revenue: revInp ? parseFloat(revInp.value || 0) : 0,
                      revenue_avg: avgInp ? parseFloat(avgInp.value || 0) : 0,
                      total_app_sale: appInp ? parseInt(appInp.value || 0) : 0,
                      percent_app_sale: pctInp
                        ? parseFloat(pctInp.value || 0)
                        : 0,
                    });
                  });
                  return revList;
                })(),
                finish: true,
              },
            }),
          },
        );
        const data = await res.json();
        if (data.result && data.result.success) {
          showToast(
            _t(
              "label:wujia.franchise.inspection_survey:toast_saved",
              "Results saved successfully!",
            ),
            false,
          );
          if (data.result.checklist_score !== undefined) {
            const lcs = document.getElementById("liveChecklistScore");
            if (lcs)
              lcs.innerText = data.result.checklist_score + " / " + maxScore;

            const les = document.getElementById("liveExamScore");
            if (les && data.result.exam_score !== undefined) {
              les.innerText = data.result.exam_score;
            }

            const lts = document.getElementById("liveTotalScore");
            if (lts) lts.innerText = data.result.total_score;

            const lg = document.getElementById("liveGrade");
            if (lg) lg.innerText = data.result.grade || "---";
          }
          // Lock only the Exam tab after saving!
          lockExamTab();
        } else {
          showCustomAlert(
            data.result
              ? data.result.error
              : _t(
                  "label:wujia.franchise.inspection_survey:toast_error",
                  "An error occurred while saving!",
                ),
          );
        }
      } catch (err) {
        showToast(
          _t(
            "label:wujia.franchise.inspection_survey:toast_network_error",
            "Server connection error!",
          ),
          true,
        );
      } finally {
        if (saveLoadingOverlay) {
          saveLoadingOverlay.style.display = "none";
        }
        if (btnFinishSurvey) {
          btnFinishSurvey.disabled = false;
          btnFinishSurvey.style.pointerEvents = "auto";
          btnFinishSurvey.style.opacity = "1";
          if (origSaveBtnHtml) btnFinishSurvey.innerHTML = origSaveBtnHtml;
        }
      }
    }

    const btnFinishSurvey = document.getElementById("btnFinishSurvey");
    if (btnFinishSurvey) {
      btnFinishSurvey.addEventListener("click", function (e) {
        e.preventDefault();
        e.stopPropagation();
        saveDataAndEvaluate();
      });
    }

    // Line Detail Modal Logic (iPad optimization)
    const lineDetailModalOverlay = document.getElementById(
      "lineDetailModalOverlay",
    );
    const lineModalClose = document.getElementById("lineModalClose");
    const lineModalBtnDone = document.getElementById("lineModalBtnDone");
    const lineModalTitle = document.getElementById("lineModalTitle");
    const lineModalContentText = document.getElementById(
      "lineModalContentText",
    );
    const lineModalPrevBadge = document.getElementById("lineModalPrevBadge");
    const lineModalPrevInspector = document.getElementById(
      "lineModalPrevInspector",
    );
    const lineModalPrevNote = document.getElementById("lineModalPrevNote");
    const lineModalPrevEvidenceWrap = document.getElementById(
      "lineModalPrevEvidenceWrap",
    );
    const lineModalPrevEvidenceImg = document.getElementById(
      "lineModalPrevEvidenceImg",
    );
    const lineModalNoteInput = document.getElementById("lineModalNoteInput");
    const lineModalTriggerUpload = document.getElementById(
      "lineModalTriggerUpload",
    );
    const lineModalImgContainer = document.getElementById(
      "lineModalImgContainer",
    );
    const lineModalImgPreview = document.getElementById("lineModalImgPreview");
    const lineModalCheck = document.getElementById("lineModalCheck");
    const lineModalCheckStatus = document.getElementById(
      "lineModalCheckStatus",
    );

    let activeRow = null;

    function openLineDetailModal(row) {
      activeRow = row;
      const contentTd = row.querySelector(".col-content");
      const contentText = contentTd ? contentTd.innerText.trim() : "";
      if (lineModalContentText) lineModalContentText.innerText = contentText;

      // Prev info
      const rawJson = row.dataset.prevInfo;
      if (rawJson && rawJson !== "null") {
        try {
          const prevData = JSON.parse(rawJson);
          if (prevData.is_pass) {
            lineModalPrevBadge.className = "badge-pass";
            lineModalPrevBadge.innerHTML =
              '<i class="fa fa-check"></i> ' +
              _t("label:wujia.franchise.inspection_survey:badge_pass", "Pass");
          } else {
            lineModalPrevBadge.className = "badge-fail";
            lineModalPrevBadge.innerHTML =
              '<i class="fa fa-times"></i> ' +
              _t("label:wujia.franchise.inspection_survey:badge_fail", "Fail");
          }
          lineModalPrevInspector.innerText =
            (prevData.planned_date || "") +
            " - " +
            (prevData.inspector || "---");
          const noteText = (prevData.note || "").trim();
          const hasNote =
            prevData.has_note ||
            (noteText &&
              noteText !== "No violation note" &&
              noteText !== "Chưa có ghi chú" &&
              noteText !== "-");
          if (hasNote && noteText) {
            lineModalPrevNote.innerHTML = `
              <div style="display: inline-flex; align-items: flex-start; gap: 8px; background: #fffbeb; border: 1px solid #fde68a; color: #b45309; padding: 8px 12px; border-radius: 8px; font-weight: 500; font-size: 13px; line-height: 1.5; width: 100%;">
                <i class="fa fa-note-sticky" style="color: #f59e0b; font-size: 16px; margin-top: 2px; flex-shrink: 0;"></i>
                <span style="word-break: break-word;">${noteText}</span>
              </div>
            `;
          } else {
            lineModalPrevNote.innerHTML =
              '<span style="color: #94a3b8; font-style: italic;">' +
              _t(
                "label:wujia.franchise.inspection_survey:no_prev_note",
                "No violation note",
              ) +
              "</span>";
          }
          if (prevData.has_evidence && prevData.evidence_url) {
            lineModalPrevEvidenceImg.src = prevData.evidence_url;
            lineModalPrevEvidenceWrap.style.display = "block";
          } else {
            lineModalPrevEvidenceWrap.style.display = "none";
          }
        } catch (e) {
          lineModalPrevBadge.className = "badge-none";
          lineModalPrevBadge.innerText = "-";
          lineModalPrevInspector.innerText = "---";
          lineModalPrevNote.innerHTML =
            '<span style="color: #94a3b8; font-style: italic;">' +
            _t(
              "label:wujia.franchise.inspection_survey:no_prev_data",
              "No previous inspection data",
            ) +
            "</span>";
          lineModalPrevEvidenceWrap.style.display = "none";
        }
      } else {
        lineModalPrevBadge.className = "badge-none";
        lineModalPrevBadge.innerText = "-";
        lineModalPrevInspector.innerText = "---";
        lineModalPrevNote.innerHTML =
          '<span style="color: #94a3b8; font-style: italic;">' +
          _t(
            "label:wujia.franchise.inspection_survey:no_prev_data",
            "No previous inspection data",
          ) +
          "</span>";
        lineModalPrevEvidenceWrap.style.display = "none";
      }

      // Note
      const noteInput = row.querySelector(".line-note");
      if (lineModalNoteInput && noteInput) {
        lineModalNoteInput.value = noteInput.value || "";
        lineModalNoteInput.readOnly = isInspectionClosed;
      }

      // Image
      const rowImgB64 = row.dataset.b64Image;
      const existingImg = row.querySelector(".img-preview");
      let imgSrc = rowImgB64 || (existingImg ? existingImg.src : "");
      if (imgSrc && imgSrc.length > 20) {
        lineModalImgPreview.src = imgSrc;
        lineModalImgContainer.style.display = "inline-flex";
      } else {
        lineModalImgContainer.style.display = "none";
      }

      if (lineModalTriggerUpload) {
        lineModalTriggerUpload.style.display = isInspectionClosed
          ? "none"
          : "inline-flex";
      }

      // Evaluation Checkbox
      const lineChk = row.querySelector(".line-check");
      if (lineModalCheck && lineChk) {
        lineModalCheck.checked = lineChk.checked;
        lineModalCheck.disabled = isInspectionClosed;
        lineModalCheckStatus.innerText = lineChk.checked
          ? _t("label:wujia.franchise.inspection_survey:badge_pass", "Pass")
          : _t("label:wujia.franchise.inspection_survey:badge_fail", "Fail");
        lineModalCheckStatus.style.color = lineChk.checked
          ? "#15803d"
          : "#ef4444";
      }

      if (lineDetailModalOverlay) lineDetailModalOverlay.style.display = "flex";
    }

    function closeLineDetailModal() {
      if (!activeRow) {
        if (lineDetailModalOverlay)
          lineDetailModalOverlay.style.display = "none";
        return;
      }
      // Save modal edits back to activeRow
      const noteInput = activeRow.querySelector(".line-note");
      if (noteInput && lineModalNoteInput) {
        noteInput.value = lineModalNoteInput.value;
        const noteInd = activeRow.querySelector(".note-indicator");
        if (noteInd) {
          noteInd.style.display = lineModalNoteInput.value.trim()
            ? "inline-flex"
            : "none";
        }
      }

      const lineChk = activeRow.querySelector(".line-check");
      if (lineChk && lineModalCheck) {
        if (lineChk.checked !== lineModalCheck.checked) {
          lineChk.checked = lineModalCheck.checked;
          updateLiveScore();
        }
      }

      if (lineDetailModalOverlay) lineDetailModalOverlay.style.display = "none";
      activeRow = null;
    }

    if (lineModalClose)
      lineModalClose.addEventListener("click", closeLineDetailModal);
    if (lineModalBtnDone)
      lineModalBtnDone.addEventListener("click", closeLineDetailModal);
    if (lineDetailModalOverlay) {
      lineDetailModalOverlay.addEventListener("click", function (e) {
        if (e.target === lineDetailModalOverlay) closeLineDetailModal();
      });
    }

    if (lineModalCheck) {
      lineModalCheck.addEventListener("change", function () {
        lineModalCheckStatus.innerText = this.checked
          ? _t("label:wujia.franchise.inspection_survey:badge_pass", "Pass")
          : _t("label:wujia.franchise.inspection_survey:badge_fail", "Fail");
        lineModalCheckStatus.style.color = this.checked ? "#15803d" : "#ef4444";
      });
    }

    if (lineModalTriggerUpload || lineModalImgPreview) {
      const handleUpload = function () {
        if (!activeRow || isInspectionClosed) return;
        const fileInput = activeRow.querySelector(".line-file");
        if (fileInput) fileInput.click();
      };
      if (lineModalTriggerUpload)
        lineModalTriggerUpload.addEventListener("click", handleUpload);
      if (lineModalImgPreview)
        lineModalImgPreview.addEventListener("click", handleUpload);
    }

    // Bind both button and item-row click to open Line Detail Modal
    document.querySelectorAll(".item-row").forEach(function (row) {
      row.addEventListener("click", function (e) {
        // If clicking checkbox in col-eval, let it toggle without opening modal
        if (
          e.target.closest(".col-eval") ||
          e.target.classList.contains("line-check")
        ) {
          return;
        }
        openLineDetailModal(row);
      });
    });

    document.querySelectorAll(".btn-open-line-detail").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.stopPropagation();
        const row = this.closest(".item-row");
        if (row) openLineDetailModal(row);
      });
    });

    // Also update photo indicator when file changes on row
    document.querySelectorAll(".item-row").forEach(function (row) {
      const fileInput = row.querySelector(".line-file");
      if (fileInput) {
        fileInput.addEventListener("change", function () {
          if (this.files && this.files[0]) {
            const reader = new FileReader();
            reader.onload = function (e) {
              row.dataset.b64Image = e.target.result;
              const photoInd = row.querySelector(".photo-indicator");
              if (photoInd) photoInd.style.display = "inline-flex";
              if (activeRow === row && lineModalImgPreview) {
                lineModalImgPreview.src = e.target.result;
                lineModalImgContainer.style.display = "inline-flex";
              }
            };
            reader.readAsDataURL(this.files[0]);
          }
        });
      }
    });
    // Attendance Management (Add, Save Member, Deactivate, Delete)
    const addStaffModalOverlay = document.getElementById(
      "addStaffModalOverlay",
    );
    const btnAddAttendanceStaff = document.getElementById(
      "btnAddAttendanceStaff",
    );
    const addStaffModalClose = document.getElementById("addStaffModalClose");
    const btnAddStaffCancel = document.getElementById("btnAddStaffCancel");
    const btnAddStaffSubmit = document.getElementById("btnAddStaffSubmit");
    const newStaffName = document.getElementById("newStaffName");
    const newStaffRole = document.getElementById("newStaffRole");
    const newStaffPhone = document.getElementById("newStaffPhone");
    const attendanceTbody = document.getElementById("attendanceTbody");
    const attendanceEmptyState = document.getElementById(
      "attendanceEmptyState",
    );

    function openAddStaffModal() {
      if (newStaffName) newStaffName.value = "";
      if (newStaffRole) newStaffRole.value = "staff";
      if (newStaffPhone) newStaffPhone.value = "";
      if (addStaffModalOverlay) addStaffModalOverlay.style.display = "flex";
      if (newStaffName) newStaffName.focus();
    }

    function closeAddStaffModal() {
      if (addStaffModalOverlay) addStaffModalOverlay.style.display = "none";
    }

    if (btnAddAttendanceStaff)
      btnAddAttendanceStaff.addEventListener("click", openAddStaffModal);
    if (addStaffModalClose)
      addStaffModalClose.addEventListener("click", closeAddStaffModal);
    if (btnAddStaffCancel)
      btnAddStaffCancel.addEventListener("click", closeAddStaffModal);

    if (btnAddStaffSubmit) {
      btnAddStaffSubmit.addEventListener("click", async function () {
        const name = newStaffName ? newStaffName.value.trim() : "";
        if (!name) {
          showCustomAlert(
            _t(
              "label:wujia.franchise.inspection_survey:alert_title",
              "Thông báo",
            ),
            _t(
              "label:wujia.franchise.inspection_survey:alert_msg_input_employee",
              "Vui lòng nhập Họ và tên nhân viên!",
            ),
          );
          return;
        }
        const role = newStaffRole ? newStaffRole.value : "staff";
        const phone = newStaffPhone ? newStaffPhone.value.trim() : "";
        const note = "";

        const origAddStaffHtml = btnAddStaffSubmit.innerHTML;
        btnAddStaffSubmit.disabled = true;
        btnAddStaffSubmit.style.pointerEvents = "none";
        btnAddStaffSubmit.innerHTML = `<i class="fa fa-spinner fa-spin me-1"></i> ${_t("label:wujia.franchise.inspection_survey:btn_adding_staff", "Đang thêm...")}`;

        const saveLoadingOverlay = document.getElementById("saveLoadingOverlay");
        if (saveLoadingOverlay) {
          const loadingTextEl = saveLoadingOverlay.querySelector("div:nth-child(2)");
          if (loadingTextEl) loadingTextEl.innerText = _t("label:wujia.franchise.inspection_survey:loading_adding_staff", "Đang thêm nhân viên...");
          saveLoadingOverlay.style.display = "flex";
        }

        try {
          const res = await fetch(
            "/franchise/inspection/do/" + inspectionId + "/attendance/add",
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                jsonrpc: "2.0",
                method: "call",
                params: {
                  inspection_id: inspectionId,
                  employee_name: name,
                  role: role,
                  phone: phone,
                  note: note,
                  is_present: true,
                },
              }),
            },
          );
          const data = await res.json();
          if (data.result && data.result.success) {
            closeAddStaffModal();
            sessionStorage.setItem(
              "wujia_survey_active_tab_" + inspectionId,
              "confirmation",
            );
            window.location.hash = "tab=confirmation";
            window.location.reload();
          } else {
            showToast(
              data.result ? data.result.error : "Error adding staff",
              true,
            );
          }
        } catch (e) {
          showToast("Network error", true);
        } finally {
          btnAddStaffSubmit.disabled = false;
          btnAddStaffSubmit.style.pointerEvents = "auto";
          btnAddStaffSubmit.innerHTML = origAddStaffHtml;
          if (saveLoadingOverlay) saveLoadingOverlay.style.display = "none";
        }
      });
    }

    function bindAttendanceRowEvents(row) {
      const chk = row.querySelector(".att-present-check");
      if (chk) chk.addEventListener("change", updatePresentCount);

      // Save to Member (->)
      const btnSaveMember = row.querySelector(".btn-save-member");
      if (btnSaveMember) {
        btnSaveMember.addEventListener("click", async function () {
          const origHtml = btnSaveMember.innerHTML;
          btnSaveMember.disabled = true;
          btnSaveMember.innerHTML = '<i class="fa fa-spinner fa-spin"></i>';
          const lineId = row.dataset.id;
          const nameInput = row.querySelector(".att-name-input");
          const roleSelect = row.querySelector(".att-role-select");
          const phoneInput = row.querySelector(".att-phone-input");
          const name = nameInput ? nameInput.value.trim() : "";
          const role = roleSelect ? roleSelect.value : "staff";
          const phone = phoneInput ? phoneInput.value.trim() : "";

          if (!name) {
            showCustomAlert(
              _t(
                "label:wujia.franchise.inspection_survey:alert_title",
                "Thông báo",
              ),
              "Vui lòng nhập Tên nhân viên trước khi lưu!",
            );
            btnSaveMember.disabled = false;
            btnSaveMember.innerHTML = origHtml;
            return;
          }

          try {
            const res = await fetch(
              "/franchise/inspection/do/" +
                inspectionId +
                "/attendance/save_member",
              {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  jsonrpc: "2.0",
                  method: "call",
                  params: {
                    inspection_id: inspectionId,
                    line_id: lineId,
                    employee_name: name,
                    role: role,
                    phone: phone,
                  },
                }),
              },
            );
            const data = await res.json();
            if (data.result && data.result.success) {
              row.dataset.memberId = data.result.member_id || "";
              const btnDeact = row.querySelector(".btn-deactivate-member");
              if (btnDeact && data.result.member_id)
                btnDeact.style.display = "inline-flex";
              showToast(
                _t(
                  "label:wujia.franchise.inspection_survey:toast_member_saved",
                  "Đã lưu thông tin vào danh sách Thành viên cửa hàng!",
                ),
                false,
              );
            } else {
              showToast(
                data.result ? data.result.error : "Error saving member",
                true,
              );
            }
          } catch (e) {
            showToast("Network error", true);
          } finally {
            btnSaveMember.disabled = false;
            btnSaveMember.innerHTML = origHtml;
          }
        });
      }

      // Deactivate Member (i)
      const btnDeactMember = row.querySelector(".btn-deactivate-member");
      if (btnDeactMember) {
        btnDeactMember.addEventListener("click", async function () {
          const confirmMsg = _t(
            "label:wujia.franchise.inspection_survey:confirm_deactivate",
            "Bạn có chắc chắn nhân viên này đã nghỉ việc (is_working = False)? Dòng này sẽ được loại bỏ khỏi đợt khảo sát.",
          );
          if (!confirm(confirmMsg)) return;

          const origHtml = btnDeactMember.innerHTML;
          btnDeactMember.disabled = true;
          btnDeactMember.innerHTML = '<i class="fa fa-spinner fa-spin"></i>';
          const lineId = row.dataset.id;

          const saveLoadingOverlay = document.getElementById("saveLoadingOverlay");
          if (saveLoadingOverlay) {
            const loadingTextEl = saveLoadingOverlay.querySelector("div:nth-child(2)");
            if (loadingTextEl) loadingTextEl.innerText = "Đang xử lý ngưng việc...";
            saveLoadingOverlay.style.display = "flex";
          }

          try {
            const res = await fetch(
              "/franchise/inspection/do/" +
                inspectionId +
                "/attendance/deactivate_member",
              {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  jsonrpc: "2.0",
                  method: "call",
                  params: {
                    inspection_id: inspectionId,
                    line_id: lineId,
                  },
                }),
              },
            );
            const data = await res.json();
            if (data.result && data.result.success) {
              sessionStorage.setItem(
                "wujia_survey_active_tab_" + inspectionId,
                "confirmation",
              );
              window.location.hash = "tab=confirmation";
              window.location.reload();
            } else {
              showToast(
                data.result ? data.result.error : "Error deactivating member",
                true,
              );
              if (saveLoadingOverlay) saveLoadingOverlay.style.display = "none";
              btnDeactMember.disabled = false;
              btnDeactMember.innerHTML = origHtml;
            }
          } catch (e) {
            showToast("Network error", true);
            if (saveLoadingOverlay) saveLoadingOverlay.style.display = "none";
            btnDeactMember.disabled = false;
            btnDeactMember.innerHTML = origHtml;
          }
        });
      }


    }

    document
      .querySelectorAll(".attendance-row")
      .forEach(bindAttendanceRowEvents);

    // ==========================================
    // Clean Pixel-Perfect Signature Pad Engine
    // ==========================================
    const signModal = document.getElementById("signModal");
    const btnOpenSignModal = document.getElementById("btnOpenSignModal");
    const sigPreviewContainer = document.getElementById("sigPreviewContainer");
    const btnCloseSignModal = document.getElementById("btnCloseSignModal");
    const btnCancelSignModal = document.getElementById("btnCancelSignModal");
    const btnSaveSignModal = document.getElementById("btnSaveSignModal");
    const btnClearModalCanvas = document.getElementById("btnClearModalCanvas");
    const btnClearSignature = document.getElementById("btnClearSignature");
    const sigCanvas = document.getElementById("signatureCanvas");
    const sigModalPlaceholder = document.getElementById("sigModalPlaceholder");
    const signaturePreviewImg = document.getElementById("signaturePreviewImg");
    const sigEmptyPrompt = document.getElementById("sigEmptyPrompt");
    const sigDataInput = document.getElementById("signatureDataInput");
    const sigStatusBadge = document.getElementById("sigStatusBadge");
    const sigDateText = document.getElementById("sigDateText");

    let isDrawing = false;
    let hasDrawn = false;
    let sigCtx = null;
    let currentDpr = 1;

    if (sigCanvas) {
      sigCtx = sigCanvas.getContext("2d");

      function initCanvasSize() {
        const rect = sigCanvas.getBoundingClientRect();
        currentDpr = window.devicePixelRatio || 1;
        if (rect.width > 0 && rect.height > 0) {
          sigCanvas.width = Math.round(rect.width * currentDpr);
          sigCanvas.height = Math.round(rect.height * currentDpr);
          sigCtx.strokeStyle = "#000080"; // Navy blue ink
          sigCtx.lineWidth = 2.4 * currentDpr;
          sigCtx.lineCap = "round";
          sigCtx.lineJoin = "round";
        }
      }

      function openModal() {
        if (isInspectionClosed) return;
        if (signModal) {
          signModal.style.display = "flex";
          initCanvasSize();
          hasDrawn = false;
          if (sigModalPlaceholder) sigModalPlaceholder.style.display = "block";
          setTimeout(initCanvasSize, 50);
          setTimeout(initCanvasSize, 150);
        }
      }

      function closeModal() {
        if (signModal) signModal.style.display = "none";
      }

      if (btnOpenSignModal) btnOpenSignModal.addEventListener("click", openModal);
      if (sigPreviewContainer) sigPreviewContainer.addEventListener("click", openModal);
      if (btnCloseSignModal) btnCloseSignModal.addEventListener("click", closeModal);
      if (btnCancelSignModal) btnCancelSignModal.addEventListener("click", closeModal);

      function getPos(e) {
        const rect = sigCanvas.getBoundingClientRect();
        let clientX = e.clientX;
        let clientY = e.clientY;
        if (e.touches && e.touches.length > 0) {
          clientX = e.touches[0].clientX;
          clientY = e.touches[0].clientY;
        } else if (e.changedTouches && e.changedTouches.length > 0) {
          clientX = e.changedTouches[0].clientX;
          clientY = e.changedTouches[0].clientY;
        }

        const scaleX = rect.width > 0 ? (sigCanvas.width / rect.width) : 1;
        const scaleY = rect.height > 0 ? (sigCanvas.height / rect.height) : 1;

        return {
          x: (clientX - rect.left) * scaleX,
          y: (clientY - rect.top) * scaleY,
        };
      }

      function startDraw(e) {
        isDrawing = true;
        hasDrawn = true;
        if (sigModalPlaceholder) sigModalPlaceholder.style.display = "none";
        const pos = getPos(e);
        sigCtx.beginPath();
        sigCtx.moveTo(pos.x, pos.y);
        e.preventDefault();
      }

      function draw(e) {
        if (!isDrawing) return;
        const pos = getPos(e);
        sigCtx.lineTo(pos.x, pos.y);
        sigCtx.stroke();
        e.preventDefault();
      }

      function endDraw(e) {
        if (!isDrawing) return;
        isDrawing = false;
      }

      sigCanvas.addEventListener("mousedown", startDraw);
      sigCanvas.addEventListener("mousemove", draw);
      window.addEventListener("mouseup", endDraw);

      sigCanvas.addEventListener("touchstart", startDraw, { passive: false });
      sigCanvas.addEventListener("touchmove", draw, { passive: false });
      window.addEventListener("touchend", endDraw);

      if (btnClearModalCanvas) {
        btnClearModalCanvas.addEventListener("click", function () {
          initCanvasSize();
          hasDrawn = false;
          if (sigModalPlaceholder) sigModalPlaceholder.style.display = "block";
        });
      }

      if (btnSaveSignModal) {
        btnSaveSignModal.addEventListener("click", function () {
          if (!hasDrawn) {
            showCustomAlert("Thông báo", "Vui lòng vẽ chữ ký trước khi đồng ý!");
            return;
          }
          const dataUrl = sigCanvas.toDataURL("image/png");
          if (sigDataInput) sigDataInput.value = dataUrl;
          if (signaturePreviewImg) {
            signaturePreviewImg.src = dataUrl;
            signaturePreviewImg.style.display = "block";
          }
          if (sigEmptyPrompt) sigEmptyPrompt.style.display = "none";
          if (btnClearSignature) btnClearSignature.style.display = "inline-flex";
          if (sigStatusBadge) sigStatusBadge.style.display = "inline-block";
          if (sigDateText) sigDateText.innerText = "Vừa ký (chưa lưu)";
          closeModal();
          showToast("Đã ghi nhận chữ ký! Hãy bấm nút 'Lưu' để hoàn tất.", false);
        });
      }

      if (btnClearSignature) {
        btnClearSignature.addEventListener("click", function () {
          if (sigDataInput) sigDataInput.value = "CLEAR";
          if (signaturePreviewImg) {
            signaturePreviewImg.src = "";
            signaturePreviewImg.style.display = "none";
          }
          if (sigEmptyPrompt) sigEmptyPrompt.style.display = "block";
          if (btnClearSignature) btnClearSignature.style.display = "none";
          if (sigStatusBadge) sigStatusBadge.style.display = "none";
          showToast("Đã xóa chữ ký. Hãy bấm nút 'Lưu' để cập nhật.", false);
        });
      }
    }

    // ==========================================
    // 3-Month Revenue Table Engine
    // ==========================================
    const revenueTbody = document.getElementById("revenueTbody");
    const btnAddRevenueRow = document.getElementById("btnAddRevenueRow");
    const revenueEmptyState = document.getElementById("revenueEmptyState");

    function getDaysInMonth(year, month) {
      return new Date(year, month, 0).getDate();
    }

    function calculateRowAvg(row) {
      const monthInp = row.querySelector(".rev-month-input");
      const revInp = row.querySelector(".rev-amount-input");
      const avgInp = row.querySelector(".rev-avg-input");
      if (!monthInp || !revInp || !avgInp) return;

      const revVal = parseFloat(revInp.value) || 0;
      const mVal = monthInp.value; // YYYY-MM
      if (mVal && mVal.includes("-")) {
        const parts = mVal.split("-");
        const y = parseInt(parts[0]);
        const m = parseInt(parts[1]);
        const days = getDaysInMonth(y, m);
        if (days > 0 && revVal > 0) {
          avgInp.value = (revVal / days).toFixed(2);
        } else {
          avgInp.value = "0";
        }
      }
    }

    function bindRevenueRowEvents(row) {
      const monthInp = row.querySelector(".rev-month-input");
      const revInp = row.querySelector(".rev-amount-input");
      const delBtn = row.querySelector(".btn-delete-rev-row");

      if (monthInp)
        monthInp.addEventListener("change", () => calculateRowAvg(row));
      if (revInp) revInp.addEventListener("input", () => calculateRowAvg(row));

      if (delBtn) {
        delBtn.addEventListener("click", function () {
          row.remove();
          if (
            revenueTbody &&
            revenueTbody.children.length === 0 &&
            revenueEmptyState
          ) {
            revenueEmptyState.style.display = "block";
          }
        });
      }
    }

    if (revenueTbody) {
      revenueTbody
        .querySelectorAll(".revenue-row")
        .forEach(bindRevenueRowEvents);
    }

    if (btnAddRevenueRow) {
      btnAddRevenueRow.addEventListener("click", function () {
        if (!revenueTbody) return;
        if (revenueEmptyState) revenueEmptyState.style.display = "none";

        // Default to current or previous month
        const now = new Date();
        const curMonthStr = now.toISOString().slice(0, 7);

        const tr = document.createElement("tr");
        tr.className = "revenue-row";
        tr.style.borderBottom = "1px solid #f1f5f9";
        tr.innerHTML = `
          <td style="padding: 8px 10px;">
            <input type="month" class="rev-month-input note-input" value="${curMonthStr}" style="padding: 6px 8px; font-size: 13px; width: 100%; font-weight: 600;" />
          </td>
          <td style="padding: 8px 10px;">
            <input type="number" step="any" class="rev-amount-input note-input" placeholder="0" style="padding: 6px 8px; font-size: 13px; width: 100%; font-weight: 600; text-align: right;" />
          </td>
          <td style="padding: 8px 10px;">
            <input type="number" step="any" class="rev-avg-input note-input" placeholder="0" style="padding: 6px 8px; font-size: 13px; width: 100%; background: #f8fafc; font-weight: 600; text-align: right;" />
          </td>
          <td style="padding: 8px 10px;">
            <input type="number" step="1" class="rev-app-sale-input note-input" placeholder="0" style="padding: 6px 8px; font-size: 13px; width: 100%; font-weight: 600; text-align: right;" />
          </td>
          <td style="padding: 8px 10px;">
            <div style="display: flex; align-items: center; gap: 4px;">
              <input type="number" step="any" class="rev-percent-input note-input" placeholder="0" style="padding: 6px 8px; font-size: 13px; width: 100%; font-weight: 600; text-align: right;" />
              <span style="font-weight: 700; color: #64748b;">%</span>
            </div>
          </td>
          <td style="padding: 8px 4px; text-align: center;">
            <button type="button" class="btn btn-sm text-danger btn-delete-rev-row" style="background: transparent; border: none; font-size: 14px; cursor: pointer;" title="Xóa dòng">
              <i class="fa fa-trash-can"></i>
            </button>
          </td>
        `;
        revenueTbody.appendChild(tr);
        bindRevenueRowEvents(tr);
      });
    }
  });
})();
