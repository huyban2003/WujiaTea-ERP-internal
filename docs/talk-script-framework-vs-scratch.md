# Kịch bản trao đổi — "viết lại từ đầu" thay vì dùng nền tảng Odoo

**Ngày:** 2026-09-08 · **Bối cảnh:** module `wujia_franchise_inspection` (nhánh `thai`, đã merge `main` @ `f11dba6`)
**Nguyên tắc:** nói bằng bằng chứng đo được, không nói bằng cảm tính; tách *việc* khỏi *người*.

> **Chủ trương đã chốt (chủ dự án, 08/09):**
> 1. Deploy đang chạy **giữ nguyên**, không chặn.
> 2. Lỗ hổng phân quyền là code của anh Thái ⇒ **anh Thái tự sửa**. Bên mình **không vá hộ**,
>    chỉ bàn giao bằng chứng + cách sửa. Lý do: người viết hiểu luồng nhất, và vá hộ thì lần sau
>    lại tái diễn.
> 3. Bên mình chỉ giữ vai **kiểm chứng lại** sau khi ảnh sửa xong.

---

## PHẦN A — Nói với anh Thái (đồng nghiệp kỹ thuật)

### A0. Mở đầu — công nhận trước

> "Phần tách module anh làm đúng hướng, `wujia_franchise` trước giờ gánh cả quản lý cửa hàng lẫn khảo sát
> là quá tải thật. Màn chấm điểm trên điện thoại cũng là việc cần và anh làm chạy được. Em merge rồi.
> Có mấy điểm em muốn thống nhất cách làm cho các phần sau, không phải bắt lỗi."

### A1. Điểm phải sửa ngay — lỗ hổng phân quyền (có bằng chứng thao tác)

> "Route `/franchise/inspection/do/<id>/save` khai `auth='user'` rồi `sudo()` mà không kiểm quyền.
> Trong Odoo, `auth='user'` **gồm cả portal user** — tức 1500 chủ cửa hàng — còn `sudo()` thì bỏ qua toàn
> bộ ACL và ir.rule."

Bằng chứng đo trên CSDL bản sao (`wujia_tea_thai`, không đụng UAT):

| Bước | Kết quả |
|---|---|
| Tạo tài khoản portal thuần (`is_internal_user=False`) | uid=75, `share=True` |
| GET `/franchise/inspection/do/1` | **404** — chỗ này có chặn ✅ |
| POST `/franchise/inspection/do/1/save` với `is_pass=false` | **`{"success": true, "total_score": 95.0, "grade": "B"}`** |
| Kiểm CSDL | dòng chấm điểm đổi từ `is_pass=t, note=''` → `is_pass=f, note='BỊ SỬA BỞI TÀI KHOẢN PORTAL'` |

> "Nghĩa là chủ cửa hàng không xem được phiếu, nhưng **sửa được điểm phiếu**. Điểm mấu chốt: phân quyền
> anh viết trong `ir.model.access.csv` **đã đúng** — portal chỉ `read`. Odoo đã chặn sẵn rồi, chính
> `sudo()` mở lại cửa. Đây là ví dụ rõ nhất cho chuyện tự làm thay nền tảng."

Cách vá đề nghị: một helper `_check_can_edit(inspection)` gọi ở đầu **cả 7 route**, kiểm
`inspector_user_id == user` hoặc `has_group('group_supervision_admin')`; và **bỏ `sudo()`** ở đường ghi để
ir.rule tự làm việc của nó. Có 11 chỗ `sudo()` trong controller, 12 chỗ trong model cần rà.

Hai điểm nhỏ cùng họ:
* `user.id in (1, 2)` — chấm quyền admin bằng **id cứng**; nên dùng `has_group`.
* Phản hồi phân biệt "phiếu không tồn tại" với "không có quyền" ⇒ cho phép dò id.

### A2. Điểm cần thống nhất — vì sao nên bám nền tảng

> "Em không nói cách anh viết là sai, nó chạy. Em nói về **giá phải trả về sau**, và mỗi món đều quy ra
> được việc cụ thể."

| Anh đang tự làm | Odoo có sẵn | Giá phải trả |
|---|---|---|
| Phân quyền bằng `sudo()` + `if` trong controller | ACL + `ir.rule` (anh đã viết đúng rồi) | **Lỗ hổng ở A1** |
| 29 chỗ `innerHTML` dựng HTML bằng chuỗi + tự viết `escapeHtml` | OWL template, tự escape | Mỗi chỗ quên `escapeHtml` là một lỗ XSS; không ai rà nổi 29 chỗ bằng mắt |
| `window.SURVEY_TRANS` — cơ chế dịch tự chế | `_t()` của Odoo + `.po` | Chuỗi không vào được quy trình dịch chung; BA đổi chữ phải sửa code |
| `<script src="...?v=1788489273">` nhúng tay | asset bundle | Đổi JS mà quên đổi số `?v=` ⇒ trình duyệt BA phục vụ bản cũ, retest ra kết quả sai. **Bên em đã dính đúng lỗi này ngày 05/09** |
| 9 biến state toàn cục quản lý tay | `useState` của OWL | Sửa một luồng dễ vỡ luồng khác mà không ai biết |
| 2.138 dòng JS, **0 test** | — | Không có gì bắt được hồi quy |

> "Cụ thể hơn: 2.138 dòng JS đó, nếu dùng OWL thì em ước chừng còn khoảng một phần ba, và phần bỏ đi
> chính là phần dễ sinh lỗi nhất — dựng HTML, escape, quản state."

### A3. Ba điểm vận hành

1. **`_bootstrap_franchise_data()`**: nạp dữ liệu cửa hàng/nhân viên **thật** từ CSV trong module lúc cài,
   dùng `print()` + `except Exception` ⇒ **seed hỏng sẽ im lặng**. Bên em đã có 3 seed chết âm thầm nhiều
   tháng vì đúng kiểu này. Đề nghị: CSV ra `scripts/`, đổi `print` → `_logger`.
2. **Google Drive**: `InstalledAppFlow` mở trình duyệt để xin quyền — **service Windows headless không chạy
   được**. `credentials.json`/`token.json` để trong thư mục module sẽ **mất sau mỗi `git pull`**. Nên dùng
   service account, đường dẫn file lấy từ `ir.config_parameter`, và khai `external_dependencies`.
3. **Bump version khi sửa module**: `wujia_franchise` bị gỡ 5 model/11 view mà giữ nguyên `19.0.4.0.2` ⇒
   server `git pull` + restart **không nạp lại XML**.

### A4. Chốt lại — bàn giao, không vá hộ

> "Em **không sửa hộ** phần này, vì anh nắm luồng rõ hơn em và sửa hộ thì lần sau dễ tái diễn.
> Em bàn giao đủ bằng chứng + cách tái hiện, anh sửa rồi báo em, em dựng lại CSDL bản sao đo lại giúp anh."

| # | Việc | Người làm | Ghi chú |
|---|---|---|---|
| 1 | Vá phân quyền 7 route (A1) | **anh Thái** | ưu tiên cao nhất, trước khi chạy thật |
| 2 | Test luồng chấm điểm + luồng quyền (5–7 test) | **anh Thái** | |
| 3 | Rà 11 `sudo()` controller + 12 `sudo()` model | **anh Thái** | bỏ ở đường ghi, giữ ở chỗ thật sự cần |
| 4 | Bỏ `user.id in (1, 2)` → `has_group` | **anh Thái** | |
| 5 | Dựng CSDL bản sao đo lại sau khi ảnh sửa | **bên em** | lặp đúng 4 bước ở A1, phải ra 403/404 |
| 6 | Màn **mới về sau** dùng OWL + component chung Portal | thống nhất chung | **màn hiện tại giữ nguyên**, không viết lại |

**Cách tái hiện gửi kèm cho ảnh** (chạy trên CSDL bản sao, **không chạy trên UAT**):

```
# 1. tạo user portal thuần (share=True, is_internal_user=False)
# 2. đăng nhập, lấy cookie
# 3. POST thẳng, bỏ qua giao diện:
curl -b cookie.txt -X POST "http://<host>/franchise/inspection/do/<id>/save" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"call","params":{"lines":[{"id":<line_id>,"is_pass":false}],"finish":false}}'
# Hiện tại: {"success": true, ...} + điểm bị tính lại  ⇒ SAI
# Sau khi vá: phải trả lỗi quyền, dữ liệu không đổi     ⇒ ĐÚNG
```

---

## PHẦN B — Nói với BA (không dùng thuật ngữ)

### B1. Tình hình

> "Tính năng khảo sát cửa hàng đã lên UAT, chị/anh test được bình thường. Có một việc kỹ thuật em cần báo
> để mình cùng quyết, vì nó ảnh hưởng tới lịch."

### B2. Vấn đề, nói bằng nghiệp vụ

> "Màn chấm điểm khảo sát hiện cho phép **tài khoản cửa hàng sửa được điểm phiếu khảo sát của chính họ**.
> Em đã thử thật trên bản sao: đăng nhập bằng tài khoản cửa hàng, đổi một tiêu chí từ *Đạt* thành *Không
> đạt*, hệ thống nhận và tính lại xếp loại. Họ không xem được phiếu, nhưng sửa được.
>
> Trên UAT thì chưa sao vì là máy nội bộ. Nhưng **không được để như vậy khi chạy thật** — vì phiếu khảo sát
> là căn cứ xếp loại cửa hàng."

### B3. Vì sao xảy ra — một câu

> "Odoo có sẵn cơ chế phân quyền và bên em đã khai đúng: cửa hàng chỉ được *xem*. Nhưng đoạn mã ghi điểm
> lại chạy ở chế độ bỏ qua phân quyền, nên cửa quyền bị mở lại."

### B4. Đề xuất

| | Việc | Người làm | Thời gian | Ảnh hưởng BA |
|---|---|---|---|---|
| 1 | Vá phân quyền (bắt buộc, trước khi chạy thật) | anh Thái | ~0,5 ngày | Không ảnh hưởng, test tiếp bình thường |
| 2 | Bổ sung test tự động cho phần khảo sát | anh Thái | ~1 ngày | Giảm lỗi lặp lại ở các đợt sau |
| 3 | Kiểm chứng lại sau khi vá | bên em | ~0,5 ngày | Có kết quả đo mới báo lại BA |
| 4 | Các màn khảo sát **mới** về sau theo chuẩn chung Portal | thống nhất chung | không phát sinh | Giao diện đồng nhất với các màn còn lại |

> "Bản đang trên UAT **vẫn test bình thường**, mình không chặn. Chỉ cần chốt là **phải vá xong mới
> đưa ra chạy thật**." 

> "Em **không đề xuất viết lại** phần đã làm — chạy được rồi, viết lại là phí. Chỉ vá chỗ hở và thống nhất
> cách làm cho phần sau."

### B5. Nếu BA hỏi "sao không phát hiện sớm?"

> "Vì phần này chưa có test tự động, và nó nằm ngoài phạm vi retest của mình — mình test *tính năng chạy
> đúng không*, chứ không test *ai được phép làm gì*. Em phát hiện khi rà soát lúc ghép mã nguồn. Đề xuất
> mục 2 ở trên chính là để lần sau máy bắt hộ."

---

## PHẦN C — Câu trả lời cho hai câu hỏi khó

**"Tự viết nhanh hơn mà, sao phải theo khuôn?"**
> Nhanh ở đoạn viết, chậm ở đoạn sửa. Ví dụ đo được: 2.138 dòng JS tự viết, 0 test, 29 chỗ dựng HTML tay —
> mỗi lần BA đổi yêu cầu là phải đọc lại toàn bộ. Còn lỗ hổng vừa rồi thì nền tảng đã chặn sẵn, chỉ vì đi
> đường vòng nên mở lại.

**"Vậy code của Thái bỏ đi hết à?"**
> Không. Phần tách module đúng, phân quyền khai đúng, tính năng chạy. Chỉ sửa 7 chỗ kiểm quyền và thống
> nhất cách làm cho các màn sau. Việc đã làm giữ nguyên.
