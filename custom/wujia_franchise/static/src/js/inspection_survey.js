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
          '<i class="fa fa-lock"></i> Đã hoàn thành &amp; Đã khóa';
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
    const tabChecklistContent = document.getElementById("tabChecklistContent");
    const tabExamContent = document.getElementById("tabExamContent");

    function switchTab(tab) {
      if (tab === "checklist") {
        if (tabChecklistContent) tabChecklistContent.style.display = "block";
        if (tabExamContent) tabExamContent.style.display = "none";
        if (tabChecklistBtn) tabChecklistBtn.classList.add("active");
        if (tabExamBtn) tabExamBtn.classList.remove("active");
      } else {
        if (tabChecklistContent) tabChecklistContent.style.display = "none";
        if (tabExamContent) tabExamContent.style.display = "block";
        if (tabChecklistBtn) tabChecklistBtn.classList.remove("active");
        if (tabExamBtn) tabExamBtn.classList.add("active");
      }
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

    // Modal "Đợt trước"
    const prevModalOverlay = document.getElementById("prevModalOverlay");
    const prevModalClose = document.getElementById("prevModalClose");

    function openPrevModal(data) {
      if (!prevModalOverlay) return;
      document.getElementById("prevInspName").innerText =
        data.inspection_name || "Đợt trước";
      document.getElementById("prevDate").innerText =
        data.planned_date || "---";
      document.getElementById("prevInspector").innerText =
        data.inspector || "---";

      const resBadge = document.getElementById("prevResultBadge");
      if (data.is_pass) {
        resBadge.className = "badge-pass";
        resBadge.innerHTML = '<i class="fa fa-check"></i> Đạt';
      } else {
        resBadge.className = "badge-fail";
        resBadge.innerHTML =
          '<i class="fa fa-times"></i> Không đạt (Trừ ' +
          (data.deduction_score || 0) +
          " điểm)";
      }

      document.getElementById("prevNote").innerText =
        data.note || "Không có ghi chú vi phạm";

      const imgContainer = document.getElementById("prevEvidenceContainer");
      const imgEl = document.getElementById("prevEvidenceImg");
      if (data.has_evidence && data.evidence_url) {
        imgEl.src = data.evidence_url;
        imgContainer.style.display = "block";
      } else {
        imgContainer.style.display = "none";
      }

      prevModalOverlay.style.display = "flex";
    }

    if (prevModalClose) {
      prevModalClose.addEventListener("click", function () {
        if (prevModalOverlay) prevModalOverlay.style.display = "none";
      });
    }
    if (prevModalOverlay) {
      prevModalOverlay.addEventListener("click", function (e) {
        if (e.target === prevModalOverlay) {
          prevModalOverlay.style.display = "none";
        }
      });
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
            alert("Chưa có thông tin dữ liệu chi tiết của đợt khảo sát trước.");
          }
        } else {
          alert(
            "Đây là đợt khảo sát đầu tiên hoặc không có dữ liệu đợt trước cho tiêu chí này.",
          );
        }
      });
    });

    // Real-time Checklist Live Score calculation
    function updateLiveScore() {
      let deductions = 0;
      document.querySelectorAll(".item-row").forEach(function (row) {
        const chk = row.querySelector(".line-check");
        if (chk && !chk.checked) {
          deductions += parseFloat(row.dataset.deduction || "0");
        }
      });
      const currentScore = Math.max(0, maxScore - deductions);
      const liveScoreEl = document.getElementById("liveChecklistScore");
      if (liveScoreEl) {
        liveScoreEl.innerText = currentScore.toFixed(1) + " / " + maxScore;
      }
    }

    document.querySelectorAll(".line-check").forEach(function (chk) {
      chk.addEventListener("change", updateLiveScore);
    });

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
          'Vui lòng nhập "Nhân viên được kiểm tra" trước khi lưu kết quả!',
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
                finish: true,
              },
            }),
          },
        );
        const data = await res.json();
        if (data.result && data.result.success) {
          showToast("Đã lưu kết quả thành công!", false);
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
            data.result ? data.result.error : "Có lỗi xảy ra khi lưu!",
          );
        }
      } catch (err) {
        showToast("Lỗi kết nối máy chủ!", true);
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
            lineModalPrevBadge.innerHTML = '<i class="fa fa-check"></i> Đạt';
          } else {
            lineModalPrevBadge.className = "badge-fail";
            lineModalPrevBadge.innerHTML =
              '<i class="fa fa-times"></i> Không đạt';
          }
          lineModalPrevInspector.innerText =
            (prevData.planned_date || "") +
            " - " +
            (prevData.inspector || "---");
          lineModalPrevNote.innerText =
            prevData.note || "Không có ghi chú vi phạm";
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
          lineModalPrevNote.innerText = "Chưa có thông tin đợt trước";
          lineModalPrevEvidenceWrap.style.display = "none";
        }
      } else {
        lineModalPrevBadge.className = "badge-none";
        lineModalPrevBadge.innerText = "-";
        lineModalPrevInspector.innerText = "---";
        lineModalPrevNote.innerText =
          "Đợt đầu tiên / Không có dữ liệu đợt trước";
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
          ? "Đạt"
          : "Không đạt (Bị trừ điểm)";
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
          ? "Đạt"
          : "Không đạt (Bị trừ điểm)";
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

    document.querySelectorAll(".btn-open-line-detail").forEach(function (btn) {
      btn.addEventListener("click", function () {
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
  });
})();
