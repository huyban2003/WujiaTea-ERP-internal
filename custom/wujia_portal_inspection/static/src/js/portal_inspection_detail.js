/** @odoo-module **/

(function () {
    function initDetailScripts() {
        // 1. Click scroll to section from Grid 2x2
        var summaryCards = document.querySelectorAll('.summary-2x2-card');
        summaryCards.forEach(function (card) {
            card.addEventListener('click', function (e) {
                var targetId = card.getAttribute('href');
                if (targetId && targetId.startsWith('#')) {
                    var targetElem = document.getElementById(targetId.substring(1));
                    if (targetElem) {
                        e.preventDefault();
                        targetElem.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                }
            });
        });

        // 2. Close button for bottom fixed action bar
        var closeBtn = document.getElementById('close_bottom_bar_btn');
        if (closeBtn) {
            closeBtn.onclick = function (e) {
                if (e) e.preventDefault();
                var bar = document.getElementById('bottom_remediation_bar');
                if (!bar) {
                    bar = document.getElementById('fixed_bottom_bar');
                }
                if (bar) {
                    bar.style.display = 'none';
                    bar.classList.add('d-none');
                }
            };
        }

        // 3. Tab Switcher
        var tabBtnChecklist = document.getElementById('tab_btn_checklist');
        var tabBtnExam = document.getElementById('tab_btn_exam');
        var pcTabBtnChecklist = document.getElementById('pc_tab_btn_checklist');
        var pcTabBtnExam = document.getElementById('pc_tab_btn_exam');
        if (tabBtnChecklist && tabBtnExam) {
            tabBtnChecklist.addEventListener('click', function () {
                switchInspectionTab('checklist');
            });
            tabBtnExam.addEventListener('click', function () {
                switchInspectionTab('exam');
            });
        }
        if (pcTabBtnChecklist && pcTabBtnExam) {
            pcTabBtnChecklist.addEventListener('click', function () {
                switchInspectionTab('checklist');
            });
            pcTabBtnExam.addEventListener('click', function () {
                switchInspectionTab('exam');
            });
        }

        // 3.5 Format Exam Questions with Blank-Filling Answers
        var questions = document.querySelectorAll('.exam-question-text');
        questions.forEach(function (q) {
            var text = q.textContent;
            var answerStr = q.getAttribute('data-answer') || '';
            var userAnswers = answerStr.split(/\r?\n/);
            
            var rawCorrect = q.getAttribute('data-correct-answers') || '[]';
            rawCorrect = rawCorrect.replace(/'/g, '"').replace(/None/g, 'null').replace(/True/g, 'true').replace(/False/g, 'false');
            var correctAnswers = [];
            try {
                correctAnswers = JSON.parse(rawCorrect);
            } catch (e) {
                console.error('Parse correct answers error:', e);
            }
            
            var blankIndex = 0;
            var newHtml = text.replace(/_{2,}/g, function (match) {
                var uAns = (userAnswers[blankIndex] !== undefined) ? userAnswers[blankIndex].trim() : '';
                var isCorrect = false;
                
                var correctForBlank = correctAnswers[blankIndex];
                if (correctForBlank !== undefined && correctForBlank !== null) {
                    if (Array.isArray(correctForBlank)) {
                        isCorrect = correctForBlank.some(function (c) {
                            return String(c).trim().toLowerCase() === uAns.toLowerCase();
                        });
                    } else {
                        isCorrect = String(correctForBlank).trim().toLowerCase() === uAns.toLowerCase();
                    }
                }
                
                var spanHtml = '';
                var displayAns = uAns || '...';
                if (isCorrect) {
                    spanHtml = '<span style="color: #16a34a; font-weight: bold; text-decoration: none; border-bottom: 2px dashed #16a34a; padding: 0 4px; margin: 0 4px;">' + displayAns + '</span>';
                } else {
                    spanHtml = '<span style="color: #dc2626; font-weight: bold; text-decoration: line-through; border-bottom: 2px dashed #dc2626; padding: 0 4px; margin: 0 4px;">' + displayAns + '</span>';
                }
                
                blankIndex++;
                return spanHtml;
            });
            
            q.innerHTML = newHtml;
        });

        function switchInspectionTab(tabName) {
            var checkTab = document.getElementById('tab_content_checklist');
            var examTab = document.getElementById('tab_content_exam');
            var checkBtn = document.getElementById('tab_btn_checklist');
            var examBtn = document.getElementById('tab_btn_exam');
            var pcCheckTab = document.getElementById('pc_tab_content_checklist');
            var pcExamTab = document.getElementById('pc_tab_content_exam');
            var pcCheckBtn = document.getElementById('pc_tab_btn_checklist');
            var pcExamBtn = document.getElementById('pc_tab_btn_exam');
            
            if (tabName === 'checklist') {
                if (checkTab) checkTab.classList.remove('d-none');
                if (examTab) examTab.classList.add('d-none');
                if (pcCheckTab) pcCheckTab.classList.remove('d-none');
                if (pcExamTab) pcExamTab.classList.add('d-none');
                
                if (checkBtn) {
                    checkBtn.style.background = '#ffffff';
                    checkBtn.style.color = '#104f7c';
                    checkBtn.classList.add('shadow-sm');
                    checkBtn.classList.remove('shadow-none');
                }
                if (examBtn) {
                    examBtn.style.background = 'transparent';
                    examBtn.style.color = '#64748b';
                    examBtn.classList.remove('shadow-sm');
                    examBtn.classList.add('shadow-none');
                }
                if (pcCheckBtn) {
                    pcCheckBtn.className = 'wj-pc-btn wj-pc-btn--primary';
                }
                if (pcExamBtn) {
                    pcExamBtn.className = 'wj-pc-btn wj-pc-btn--secondary';
                }
            } else {
                if (checkTab) checkTab.classList.add('d-none');
                if (examTab) examTab.classList.remove('d-none');
                if (pcCheckTab) pcCheckTab.classList.add('d-none');
                if (pcExamTab) pcExamTab.classList.remove('d-none');
                
                if (checkBtn) {
                    checkBtn.style.background = 'transparent';
                    checkBtn.style.color = '#64748b';
                    checkBtn.classList.remove('shadow-sm');
                    checkBtn.classList.add('shadow-none');
                }
                if (examBtn) {
                    examBtn.style.background = '#ffffff';
                    examBtn.style.color = '#104f7c';
                    examBtn.classList.add('shadow-sm');
                    examBtn.classList.remove('shadow-none');
                }
                if (pcCheckBtn) {
                    pcCheckBtn.className = 'wj-pc-btn wj-pc-btn--secondary';
                }
                if (pcExamBtn) {
                    pcExamBtn.className = 'wj-pc-btn wj-pc-btn--primary';
                }
            }
        }

        // 4. Remediation Form logic
        var remediationForms = document.querySelectorAll('form[action="/portal/inspection/remediation/submit"]');
        remediationForms.forEach(function (form) {
            var imageInput = form.querySelector('.image-upload-input');
            var dropzone = form.querySelector('.upload-dropzone');
            
            if (imageInput) {
                imageInput.addEventListener('change', function () {
                    if (imageInput.files && imageInput.files[0]) {
                        var reader = new FileReader();
                        reader.onload = function (e) {
                            var placeholder = form.querySelector('.upload-placeholder');
                            if (placeholder) placeholder.classList.add('d-none');
                            var preview = form.querySelector('.upload-preview-img');
                            if (preview) {
                                preview.src = e.target.result;
                                preview.classList.remove('d-none');
                            }
                        }
                        reader.readAsDataURL(imageInput.files[0]);
                    }
                });
            }

            if (dropzone && imageInput) {
                dropzone.addEventListener('click', function () {
                    imageInput.click();
                });
            }

            var noteInput = form.querySelector('.remediation-note-input');
            if (noteInput) {
                noteInput.addEventListener('keyup', function () {
                    var counter = form.querySelector('.char-count');
                    if (counter) {
                        counter.innerText = noteInput.value.length;
                    }
                });
            }

            form.addEventListener('submit', function (e) {
                e.preventDefault();
                var formData = new FormData(form);
                var csrfToken = (window.odoo && window.odoo.csrf_token) ? window.odoo.csrf_token : '';
                if (csrfToken) {
                    formData.set('csrf_token', csrfToken);
                }

                fetch('/portal/inspection/remediation/submit', {
                    method: 'POST',
                    body: formData
                }).then(function (response) {
                    var contentType = response.headers.get('content-type') || '';
                    if (contentType.indexOf('application/json') !== -1) {
                        return response.json();
                    }
                    return { status: 'redirect', message: 'Phiên đăng nhập hết hạn, vui lòng đăng nhập lại.' };
                }).then(function (data) {
                    if (data.status === 'redirect') {
                        window.location.href = '/web/login';
                        return;
                    }
                    if (data.status === 'success') {
                        if (data.franchise_code) {
                            var franchiseCodeElem = document.getElementById('modal_franchise_code');
                            if (franchiseCodeElem) franchiseCodeElem.innerText = data.franchise_code;
                        }
                        if (data.category_name) {
                            var catNameElem = document.getElementById('modal_category_name');
                            if (catNameElem) catNameElem.innerText = data.category_name;
                        }
                        if (data.submit_time) {
                            var submitTimeElem = document.getElementById('modal_submit_time');
                            if (submitTimeElem) submitTimeElem.innerText = data.submit_time;
                        }
                        if (data.detail_url) {
                            var detailUrlElem = document.getElementById('modal_detail_url');
                            if (detailUrlElem) detailUrlElem.setAttribute('href', data.detail_url);
                        }
                        const modal = document.getElementById('remediation_success_modal');
                        if (modal) {
                            modal.classList.add('show-modal');
                        }
                    } else {
                        alert(data.message || 'Gửi phản hồi thất bại, vui lòng thử lại.');
                    }
                }).catch(function (err) {
                    console.error('Submit error:', err);
                    alert('Có lỗi xảy ra khi gửi phản hồi, vui lòng thử lại.');
                });
            });
        });

        function previewRemediationImage(input) {
            if (input.files && input.files[0]) {
                var reader = new FileReader();
                reader.onload = function (e) {
                    var placeholder = document.getElementById('upload_placeholder');
                    if (placeholder) placeholder.classList.add('d-none');
                    var preview = document.getElementById('upload_preview_img');
                    if (preview) {
                        preview.src = e.target.result;
                        preview.classList.remove('d-none');
                    }
                }
                reader.readAsDataURL(input.files[0]);
            }
        }

        function countChars(textarea) {
            var counter = document.getElementById('char_count');
            if (counter) {
                counter.innerText = textarea.value.length;
            }
        }

        // 5. Image Lightbox Modal
        var previewImages = document.querySelectorAll('.wj-img-zoom');
        var lightbox = document.getElementById('wj_lightbox');
        var lightboxImg = document.getElementById('wj_lightbox_img');
        if (lightbox && lightboxImg) {
            previewImages.forEach(function (img) {
                img.style.cursor = 'zoom-in';
                img.addEventListener('click', function (e) {
                    if (img.src && !img.classList.contains('d-none') && img.getAttribute('src') !== '#') {
                        e.stopPropagation();
                        lightboxImg.src = img.src;
                        lightbox.style.display = 'block';
                    }
                });
            });
        }

        // 6. Back to Top Button Logic (Show on scroll, auto-hide after 3s of inactivity)
        var backToTopBtn = document.getElementById('wj_back_to_top_btn');
        if (backToTopBtn) {
            var scrollTimeout = null;
            
            window.addEventListener('scroll', function () {
                var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                
                if (scrollTop > 300) {
                    backToTopBtn.classList.add('show-btn');
                    
                    // Clear previous timeout
                    if (scrollTimeout) {
                        clearTimeout(scrollTimeout);
                    }
                    
                    // Set new timeout to hide the button after 3 seconds of no scrolling
                    scrollTimeout = setTimeout(function () {
                        backToTopBtn.classList.remove('show-btn');
                    }, 3000);
                } else {
                    backToTopBtn.classList.remove('show-btn');
                    if (scrollTimeout) {
                        clearTimeout(scrollTimeout);
                    }
                }
            });
            
            backToTopBtn.addEventListener('click', function () {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDetailScripts);
    } else {
        initDetailScripts();
    }
})();
