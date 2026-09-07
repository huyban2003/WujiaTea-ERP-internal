# Câu hỏi BA — `CMP-CH-001` CardHeader: chỗ có **HAI** vùng phụ bên phải

**Gửi:** BA · **Từ:** Dev · **Ngày:** 04/09/2026
**Issue liên quan:** `UI-CARDHEADER-001` (STT 125, tab `5. Issue List`)
**Trạng thái:** đang chặn 3 call site — code đã sẵn, chỉ chờ phán quyết

---

## Vì sao phải hỏi

Spec `CMP-CH-001` quy định CardHeader có **tối đa MỘT** vùng phụ bên phải tiêu đề
(`action` / `control` / `meta`). Trong mã nguồn có **3 chỗ mang HAI vùng**. Dev **không tự
quyết** vì mỗi cách xử cho ra bố cục khác nhau và đều nhìn thấy được, nên gộp một lượt hỏi.

Ba chỗ này đang **giữ nguyên markup cũ**, không lỗi hiển thị, chỉ là chưa dùng component chung.
Chúng vẫn là **heading thật** (`<h2>`/`<h3>`), không phải giả-heading — nên không vi phạm phần
"bỏ giả-heading" của issue.

**Tiền lệ đã có:** ở D3a Dev tự xử một trường hợp tương tự bằng cách **để cả hai vùng đứng
ngoài CardHeader**, coi chúng là nội dung card. Cách đó giữ nguyên hiển thị và đúng chữ spec,
nhưng chưa được BA xác nhận là hướng chuẩn. Ba chỗ dưới đây chờ chính câu trả lời đó.

---

## Chỗ 1 — Thẻ đầu trang "Thông tin cửa hàng" (treo từ D3a, 27/08)

**Đường dẫn:** `/portal/franchise-information` (PC) ·
`wujia_portal_base/views/portal_franchise_information.xml:28`

```
┌────────────────────────────────────────────────────────────────────────┐
│ [icon]  HN-01 · Cửa hàng 125 Cầu Giấy          ┌──────────────────────┐│
│         Cửa hàng nhượng quyền đang thao tác     │ Quyền xem hiện tại   ││  ← vùng B
│         [Đang hoạt động] [Khu vực Hà Nội]       │ Owner / Manager      ││
│         └── vùng A                              └──────────────────────┘│
└────────────────────────────────────────────────────────────────────────┘
```

| | Nội dung | Bản chất |
|---|---|---|
| **Vùng A** | 2 badge: trạng thái cửa hàng + khu vực | nhãn trạng thái |
| **Vùng B** | Ô "Quyền xem hiện tại" (nhãn + giá trị) | khối thông tin |

**Dev đề xuất:** `trailing = vùng A` (badge trạng thái — đúng vai "meta" của spec), **vùng B
xuống làm nội dung card**. Lý do: vùng B là một cặp nhãn–giá trị, cùng loại với các cặp KV khác
trong trang, không phải trạng thái của chính tiêu đề.

---

## Chỗ 2 — "Người tham gia" trong màn Đăng ký thi (PC)

**Đường dẫn:** `/portal/exam/register` (PC) ·
`wujia_portal_exam/views/portal_exam.xml:396`

```
┌────────────────────────────────────────────────────────────────────────┐
│ Người tham gia            Ghi chú (không bắt buộc)                     │
│ Nhập trực tiếp thông tin  ┌──────────────────────┐  ┌───────────────┐  │
│ của từng người dự thi.    │                      │  │ + Thêm người  │  │
│                           └──────────────────────┘  └───────────────┘  │
│                            └── vùng A                └── vùng B        │
└────────────────────────────────────────────────────────────────────────┘
```

| | Nội dung | Bản chất |
|---|---|---|
| **Vùng A** | Ô nhập "Ghi chú (không bắt buộc)" | **control nhập liệu** |
| **Vùng B** | Nút "+ Thêm người" | **hành động** |

**Khó hơn Chỗ 1:** cả hai đều là thành phần **tương tác**, không cái nào rõ ràng là "nội dung
card" để đẩy xuống như vùng B của Chỗ 1.

**Dev đề xuất:** `trailing = nút "Thêm người"` (hành động chính của khối), **ô Ghi chú xuống
thành một dòng riêng ngay dưới header, chiếm hết bề rộng**. Lý do: ô Ghi chú là **dữ liệu của
phiếu đăng ký**, không phải điều khiển của tiêu đề; và ở màn hình hẹp nó cần cả bề rộng.

> ℹ️ Xin BA lưu ý: Dev vừa vá bố cục màn này ở laptop **dưới 1600px** (04/09) — lịch và khung giờ
> nay **xếp dọc** thay vì hai cột. Nếu BA chọn phương án cho Chỗ 2, xin xác nhận luôn cách xếp ô
> Ghi chú ở khổ hẹp.

---

## Chỗ 3 — Thẻ "Nhân sự" trong Đăng ký thi (mobile)

**Đường dẫn:** `/portal/exam/register` bước 3 (mobile) ·
`wujia_portal_exam/views/portal_exam.xml:809`

```
┌──────────────────────────────────┐
│ Nhân sự 1   [Bắt buộc]     [🗑]  │
│             └ vùng A       └ B   │
│ ┌──────────────────────────────┐ │
│ │ Họ và tên                    │ │
│ └──────────────────────────────┘ │
└──────────────────────────────────┘
```

| | Nội dung | Bản chất |
|---|---|---|
| **Vùng A** | Nhãn "Bắt buộc" | nhãn trạng thái |
| **Vùng B** | Nút xóa người (thùng rác) | hành động |

**⚠️ Chỗ này rủi ro kỹ thuật cao nhất trong cả cụm.** Khối markup này bị JavaScript **nhân bản
làm khuôn** để dựng người thứ 2, 3, 4 khi bấm "Thêm người". Đổi cấu trúc của nó là đổi khuôn —
sai một chút thì **người mới thêm bị dựng lỗi mà không có thông báo nào**. Dev sẽ khóa lại bằng
test tự động trước khi sửa, nhưng cần BA chốt hình dáng trước.

**Dev đề xuất:** `trailing = nút xóa` (hành động), **nhãn "Bắt buộc" nhập vào phần phụ đề của
tiêu đề**. Lý do: "Bắt buộc" mô tả chính người đó, thuộc về tiêu đề hơn là đứng riêng.

---

## Chỗ KHÔNG hỏi — Dev đã tự quyết theo tiền lệ

`portal_exam.xml:858` `wujia-mexam-sheet-title` — tiêu đề của **bảng trượt từ dưới lên**
(bottom-sheet), không phải tiêu đề card trong trang ⇒ **loại**, theo đúng tiền lệ đã áp cho
`mobile_bottomnav.xml:58`. Nêu ở đây để BA biết, không cần trả lời.

---

## Dev cần gì ở BA

Với **mỗi chỗ**, xin BA chọn một:

1. **Đồng ý đề xuất của Dev** (nhanh nhất — Dev làm ngay ở phiên D3 kế tiếp), hoặc
2. **Chỉ định vùng nào là trailing**, vùng còn lại xử ra sao, hoặc
3. **Nới spec**: cho phép CardHeader mang **2 vùng phụ**, kèm quy tắc thứ tự và cách xuống dòng
   ở màn hẹp (nếu chọn hướng này thì Dev sẽ sửa **chính component dùng chung**, ảnh hưởng cả
   61 chỗ đã migrate ⇒ cần BA nói rõ).

**Không gấp** — 3 chỗ này đang hiển thị bình thường, không lỗi. Chúng chỉ chặn phần "dùng chung
component" của issue `UI-CARDHEADER-001`, mà issue đó còn nhiều màn khác chưa làm nên Dev vẫn
có việc chạy song song.
