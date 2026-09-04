/* ==========================================================================
   Wujia Franchise - Supervision Inspection Report Scripts
   ========================================================================== */

(function () {
  "use strict";

  let allTranslations = {};

  function initTranslations() {
    try {
      const rawEl = document.getElementById("reportTransJson");
      if (rawEl) {
        allTranslations = JSON.parse(rawEl.textContent || "{}");
      }
    } catch (e) {
      console.error("Failed to parse report translations JSON:", e);
    }
  }

  function applyLanguage(lang) {
    initTranslations();
    const dict = allTranslations[lang];
    if (!dict) {
      console.warn("No dictionary found for language:", lang);
      return;
    }

    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      if (dict[key]) {
        el.innerHTML = dict[key];
      }
    });

    applyDynamicTitle();
  }

  function getFormattedPdfName() {
    const storeEl = document.querySelector(".store-name-sub");
    const dateEl = document.querySelector(".report-date-text strong");
    const selLang = document.getElementById("selReportLang");
    const curLang = selLang ? selLang.value : "vi_VN";

    let reportPrefix = "Báo cáo Khảo sát Giám sát";
    if (curLang === "zh_CN" || (curLang && curLang.includes("zh"))) {
      reportPrefix = "加盟門市督導報告";
    } else if (curLang === "th_TH" || (curLang && curLang.includes("th"))) {
      reportPrefix = "รายงานการตรวจประเมินร้านสาขา";
    }

    let storeCode = "";
    if (storeEl) {
      const rawText = storeEl.innerText.trim();
      const match = rawText.match(/\((.*?)\)/);
      if (match && match[1] && match[1] !== "---") {
        storeCode = match[1].trim();
      } else {
        storeCode = rawText.replace(/\(.*?\)/g, "").trim();
      }
    }
    let dateStr = "";
    if (dateEl) {
      dateStr = dateEl.innerText.trim().replace(/\//g, "-");
    }
    if (storeCode && dateStr) {
      return `${reportPrefix} [${storeCode}] [${dateStr}]`;
    }
    return document.title || reportPrefix;
  }

  function applyDynamicTitle() {
    const formattedTitle = getFormattedPdfName();
    document.title = formattedTitle;
    try {
      if (window.parent && window.parent.document) {
        window.parent.document.title = formattedTitle;
      }
      if (window.top && window.top.document) {
        window.top.document.title = formattedTitle;
      }
    } catch (e) {}
  }

  function maskUrl() {
    try {
      if (window.history && window.history.replaceState) {
        window.history.replaceState({}, "", "/wujiateavn");
      }
    } catch (e) {}
  }

  function setupEvents() {
    initTranslations();
    applyDynamicTitle();

    window.addEventListener("beforeprint", function () {
      maskUrl();
      applyDynamicTitle();
    });

    const btnPrint = document.getElementById("btnPrintReport");
    if (btnPrint) {
      btnPrint.onclick = function () {
        maskUrl();
        applyDynamicTitle();
        window.print();
      };
    }

    const selLang = document.getElementById("selReportLang");
    if (selLang) {
      selLang.onchange = function () {
        const langVal = this.value;
        applyLanguage(langVal);
      };
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setupEvents);
  } else {
    setupEvents();
  }
})();
