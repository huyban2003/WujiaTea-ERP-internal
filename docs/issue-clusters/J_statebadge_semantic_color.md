# Đề xuất issue MỚI — nhãn trạng thái mất màu ngữ nghĩa trên bản máy tính

**Dev phát hiện 04/09/2026** khi soi ảnh chụp cụm D3e. **Chưa có dòng trên sheet** — nhờ BA mở
issue rồi Dev làm; chủ dự án đã chốt **tách riêng, không gộp vào D3f** (D3f là chuẩn hoá cấu trúc
tiêu đề, trộn một fix màu vào sẽ làm nhiễu bảng đối chiếu ảnh trước/sau của cả cụm).

## Hiện tượng

`/portal/return/<mã>` trên máy tính: nhãn trạng thái ("Đã Gửi", …) **xám mờ**, dính sát lề trên
của thẻ, không mang màu theo trạng thái như bản điện thoại của chính màn đó.

## Root cause — đã truy xong, không phải phỏng đoán

`portal_return_detail.xml:18`:

```xml
<span t-attf-class="badge state-badge #{lbl[1]}" t-out="lbl[0]"/>
```

`lbl[1]` là một lớp `wujia-badge-*` mang màu ngữ nghĩa (khai ở `_components.css` ~dòng 148).
Nhưng thẻ mang **thêm** lớp cũ `.state-badge`, mà lớp này khai **SAU** trong **cùng một file**,
**cùng đặc hiệu (0,1,0)**:

```css
.state-badge { background-color: var(--wujia-muted-bg); color: var(--wujia-text-secondary); }
```

⇒ đến sau nên thắng, **nuốt sạch màu ngữ nghĩa**.

## Phạm vi

| Chỗ | Tình trạng |
|---|---|
| `portal_return_detail.xml:18` | **Lỗi** |
| `portal_info_request_detail.xml:23` | **Lỗi — cùng một bệnh** |
| `portal_franchise_profile.xml:45` | Lành: dùng `state-#{status}` khai SAU `.state-badge` |
| `portal_return_detail.xml:243` (nhánh điện thoại) | Lành: **đã dùng đúng cách** |

## Cách sửa

Bỏ `badge state-badge`, chỉ để `wujia-badge` + lớp ngữ nghĩa — **đúng như dòng 243 của chính
`portal_return_detail.xml`** đang làm. 2 dòng, không đụng CSS dùng chung.

## Retest

Mở `/portal/return/<mã>` và `/portal/info-request/<mã>` trên máy tính ở 1920 và 1440: nhãn trạng
thái phải cùng màu với **chính màn đó xem trên điện thoại**, và cùng màu với nhãn cùng trạng thái
ở màn danh sách. Đổi qua đủ các trạng thái để mỗi trạng thái ra đúng màu của nó.

## LIMIT

Đây là component **`CMP-SB-001` StatusBadge**, một trong **20/23 component BA chưa viết spec**
(§13 compact summary cấm tự đoán px/màu). Đề xuất trên **chỉ sửa lỗi cascade** — trả lại đúng màu
mà chính hệ thống đã khai sẵn — **không tự đặt màu hay kích thước mới**. Việc chuẩn hoá thật sự
component này phải chờ spec BA.
