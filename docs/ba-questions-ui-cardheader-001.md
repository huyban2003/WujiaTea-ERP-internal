# Gửi BA — 5 câu hỏi còn treo của `UI-CARDHEADER-001` (STT 125)

**Từ:** Dev · **Gửi:** BA · **Ngày:** 04/09/2026
**Issue:** `UI-CARDHEADER-001`, tab `5. Issue List` dòng 118 — đang ở **`Need Clarification`**
**Mục đích của văn bản này:** gom **một lượt** tất cả chỗ Dev không tự quyết được, để BA trả lời
xong là gỡ được trạng thái `Need Clarification` và Dev chạy tiếp.

---

## Tình hình một dòng

Việc "đưa mọi tiêu đề nằm trong thẻ về **một khuôn chung**" đã làm được **95 trên 105 chỗ**, qua
sáu đợt từ 27/08 đến 04/09, và đã cài lên máy chủ thử nghiệm. Đợt cuối còn kiểm lại bằng **ảnh
chụp thật** ở 31 màn × 4 khổ màn hình: không màn nào vỡ, không màn nào cuộn ngang, không lỗi.

**Mười chỗ còn lại không phải vì khó làm, mà vì mỗi chỗ đều có một câu hỏi nghiệp vụ Dev không
có quyền tự trả lời.** Năm câu hỏi dưới đây gom trọn mười chỗ đó. Tất cả đang hiển thị bình
thường, **không có lỗi nào đang xảy ra với người dùng** — nên BA không cần vội, nhưng chưa trả
lời thì Dev không thể tuyên bố issue này xong 100%.

---

## Câu hỏi (a) — Thẻ đầu trang "Thông tin cửa hàng" có **hai** khối bên phải

**Ở đâu:** trang *Thông tin cửa hàng* trên máy tính (`/portal/franchise-information`).

```
┌──────────────────────────────────────────────────────────────────────────┐
│ [icon]  HN-01 · Cầu Giấy                        ┌──────────────────────┐ │
│         Cửa hàng nhượng quyền đang thao tác     │ Quyền xem hiện tại   │ │ ← khối B
│         [Đang hoạt động] [Khu vực Hà Nội]       │ Owner / Manager      │ │
│         └── khối A                              └──────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
```

**Vướng ở đâu:** bảng thành phần của BA cho phép tiêu đề thẻ có **tối đa MỘT** khối phụ bên phải.
Chỗ này đang có **hai**: dãy nhãn trạng thái (A) và ô "Quyền xem hiện tại" (B).

**Dev đang làm tạm thế nào:** để **cả hai khối đứng ngoài** khuôn tiêu đề, coi chúng là nội dung
của thẻ. Cách này giữ nguyên hiển thị y như cũ, không sai chữ nào của bảng thành phần, và không
có rủi ro hỏng — nhưng nó nghĩa là chỗ này **chưa dùng khuôn chung**, tức chưa đạt mục tiêu issue.

**Dev đề xuất:** lấy **khối A (dãy nhãn trạng thái)** làm khối phụ bên phải của tiêu đề, còn
**khối B xuống làm nội dung thẻ**. Lý do: khối B là một cặp *nhãn – giá trị*, cùng loại với mọi
cặp thông tin khác trong trang; còn nhãn trạng thái thì mô tả chính cửa hàng đang nêu ở tiêu đề.

**BA chọn một:** ☐ đồng ý đề xuất · ☐ chỉ định khối nào lên trên, khối kia xử ra sao ·
☐ nới bảng thành phần cho phép **hai** khối phụ *(nếu chọn hướng này, Dev phải sửa chính khuôn
dùng chung, ảnh hưởng cả 95 chỗ đã làm — mong BA nói rõ thứ tự hai khối và cách xuống dòng ở
màn hình hẹp)*

---

## Câu hỏi (b) — Hai yêu cầu trong bảng thành phần đang chỏi nhau

**Bảng thành phần ghi đồng thời hai điều:**

1. Tiêu đề dài thì **xuống tối đa 2 dòng**;
2. **Không được cắt chữ bằng ba chấm** (`…`).

**Vì sao chỏi nhau:** muốn chặn ở 2 dòng thì phần chữ vượt quá **bắt buộc** phải biến mất bằng
cách nào đó — mà cách duy nhất trình duyệt có là cắt bằng ba chấm. Giữ đủ chữ thì phải cho phép
tràn sang dòng thứ 3. Không thể cùng lúc có cả hai.

**Dev đang chọn:** **luôn hiện đủ chữ**, không cắt.

**Số đo thật để BA yên tâm:** hai dòng chứa được khoảng **64 ký tự trên điện thoại** và
**96 ký tự trên máy tính**. Tiêu đề dài nhất hiện có trong toàn hệ thống là **22 ký tự**. Nghĩa
là trên thực tế **mọi tiêu đề đang có đều nằm gọn trong MỘT dòng** — cuộc tranh chấp này hiện chỉ
tồn tại trên giấy, chưa từng xảy ra trên màn hình.

**BA chọn một:** ☐ giữ như Dev đang làm, sửa bảng thành phần bỏ mục "tối đa 2 dòng" ·
☐ ưu tiên chặn 2 dòng, chấp nhận cắt bằng ba chấm · ☐ giữ cả hai câu chữ nhưng ghi rõ "2 dòng"
chỉ là khuyến nghị thiết kế, không phải luật kỹ thuật

---

## Câu hỏi (c) — Ba chỗ đang là "tiêu đề mục", BA từng chỉ đích danh, giờ lại giống "tiêu đề thẻ"

Ba chỗ này **treo từ đợt trước** (cụm C8, `UI-SECTIONHEADER-001`) và Dev cố ý không quyết lại.

| Chỗ | Hiện đang là | Vì sao phân vân |
|---|---|---|
| Tiêu đề danh sách ở trang **Giao hàng** và **Đặt hàng** (máy tính) | tiêu đề **mục** | Chúng **nằm bên trong thẻ**, nên theo bảng thành phần mới thì phải là tiêu đề **thẻ**. Nhưng chính BA đã chỉ đích danh chúng là tiêu đề **mục** ở đợt trước, và Dev đã làm đúng như vậy rồi |
| Dòng **"THÔNG TIN CHUYỂN KHOẢN"** ở trang Công nợ | tiêu đề **mục**, chữ nhỏ 11px viết hoa | Đây là chỗ **BA nêu lại đích danh** trong chính yêu cầu tiêu đề thẻ (*"Debt summary dùng label 11px viết hoa"*) ⇒ nhiều khả năng BA muốn đổi sang tiêu đề thẻ. Nhưng ô chứa nó bị khoá chiều cao cứng 150px, đổi cỡ chữ là đổi bố cục cả ô |
| Tiêu đề **"Danh sách phiếu khảo sát"** | tiêu đề **mục** | Cùng loại với hai chỗ trên; đợt trước đã ghi `Need Clarification` và chưa có câu trả lời |

**Vì sao Dev không tự quyết:** đổi loại tiêu đề là đổi cỡ chữ, độ đậm và khoảng cách — người dùng
nhìn thấy ngay. Và quan trọng hơn: **hai yêu cầu của BA đang chỉ vào cùng một chỗ với hai kết
luận khác nhau**. Dev chọn bên nào cũng là làm sai một trong hai.

**BA chọn một:** ☐ giữ nguyên cả ba là tiêu đề **mục** (Dev không đụng nữa, ghi vào bảng thành
phần là ngoại lệ có chủ đích) · ☐ đổi cả ba sang tiêu đề **thẻ** · ☐ đổi riêng dòng
"THÔNG TIN CHUYỂN KHOẢN", hai chỗ kia giữ nguyên

---

## Câu hỏi (d) — "Thẻ bộ lọc" là **dựng mới**, không phải chuyển đổi

**Bảng thành phần có mô tả tiêu đề cho thẻ bộ lọc.** Nhưng Dev đã rà toàn bộ hệ thống:
**hiện chưa màn nào có tiêu đề trên thẻ bộ lọc cả** — các thẻ bộ lọc đang chỉ có các ô chọn, không
có dòng tiêu đề nào ở trên.

**Nghĩa là:** đây **không phải** việc "đưa cái đang có về khuôn chung" như phần còn lại của issue,
mà là **thêm mới một dòng tiêu đề vào những màn hiện chưa có**. Đó là thay đổi người dùng nhìn
thấy ngay ở nhiều màn, và nó làm mỗi thẻ bộ lọc **cao thêm** — trên điện thoại, chỗ cao thêm đó
đẩy nội dung chính xuống dưới.

**Dev không tự làm** vì thêm chữ mới lên màn hình là quyết định của BA, không phải của Dev.

**BA chọn một:** ☐ **có**, thêm tiêu đề cho thẻ bộ lọc — xin BA cho **chữ cụ thể** và
**danh sách màn** cần thêm · ☐ **không**, bỏ mục thẻ bộ lọc khỏi phạm vi issue này ·
☐ tách thành **một mục riêng** làm sau, để `UI-CARDHEADER-001` đóng được

---

## Câu hỏi (e) — Bốn chỗ Dev cố ý chưa đụng, cùng một lý do với câu (a)

Cả bốn đều có **hai** khối bên phải tiêu đề trong khi bảng thành phần cho tối đa một.

| Chỗ | Hai khối bên phải là gì | Ghi chú riêng |
|---|---|---|
| Thẻ đầu trang *Thông tin cửa hàng* — hai vị trí trong cùng một thẻ | dãy nhãn trạng thái + ô "Quyền xem hiện tại" | Chính là chỗ ở **câu (a)**; trả lời câu (a) là xong luôn hai vị trí này |
| Khối **"Người tham gia"** — màn Đăng ký thi trên máy tính | ô nhập *Ghi chú (không bắt buộc)* + nút *+ Thêm người* | **Khó hơn câu (a):** cả hai đều là thứ bấm/gõ được, không cái nào rõ ràng là "nội dung thẻ" để đẩy xuống. Dev đề xuất: nút *Thêm người* lên trên, ô *Ghi chú* xuống thành một dòng riêng chiếm hết bề rộng — vì Ghi chú là **dữ liệu của phiếu đăng ký**, không phải điều khiển của tiêu đề |
| Thẻ **"Nhân sự 1, 2, 3…"** — màn Đăng ký thi trên điện thoại | nhãn *Bắt buộc* + nút xoá người | ⚠️ **Rủi ro kỹ thuật cao nhất cả cụm.** Khối này bị hệ thống **nhân bản làm khuôn** để dựng người thứ 2, 3, 4 khi bấm *Thêm người*. Đổi cấu trúc của nó là đổi khuôn — sai một chút thì **người mới thêm bị dựng hỏng mà không hiện thông báo nào**. Dev sẽ khoá lại bằng phép thử tự động trước khi sửa, nhưng cần BA chốt hình dáng trước. Dev đề xuất: nút xoá lên trên, nhãn *Bắt buộc* nhập vào phần phụ đề của tiêu đề |

**Một chỗ Dev đã tự quyết, nêu để BA biết chứ không cần trả lời:** tiêu đề của **bảng trượt từ
dưới lên** ở màn Đăng ký thi — đây không phải tiêu đề thẻ trong trang mà là tiêu đề của một lớp
phủ, nên loại khỏi phạm vi, đúng theo tiền lệ đã áp cho thanh điều hướng dưới đáy và khay thông báo.

**BA chọn một cho mỗi chỗ:** ☐ đồng ý đề xuất của Dev · ☐ chỉ định khối nào lên trên ·
☐ nới bảng thành phần cho phép hai khối *(xem cảnh báo ở câu (a))*

> Chi tiết kỹ thuật đầy đủ kèm sơ đồ từng chỗ: `docs/ba-question-cardheader-trailing.md`
> (văn bản này là bản gộp, văn bản kia là phụ lục).

---

## Hai việc Dev đề nghị BA **mở thành mục riêng** (không nằm trong issue này)

### 1. Màn phiếu giám sát cửa hàng vẫn đang **tự đẻ tài khoản trùng**

Ở màn nhập phiếu giám sát cửa hàng, khi ghi tên một nhân sự, hệ thống **tìm người theo TÊN** rồi
nếu không thấy thì **tự tạo một tài khoản mới với tên đăng nhập ngẫu nhiên** dạng
`nguyen.van.a.4271@wujiatea.internal`.

**Hai vấn đề:** tìm theo tên thì hai người trùng tên bị gộp làm một; còn tự đặt tên đăng nhập
ngẫu nhiên thì mỗi lần gõ sai chính tả một chữ là **đẻ thêm một tài khoản nữa**.

Đây đúng là kiểu sinh tài khoản trùng mà việc *Onboarding cửa hàng* (`WJ-FRANCHISE-003`) vừa dẹp
xong ở luồng mở cửa hàng. Nhưng chỗ này nằm ở **luồng giám sát**, là phạm vi khác, có luồng
nghiệp vụ và người dùng khác — Dev cố ý không sửa kèm để không kéo theo phải kiểm thử lại cả
phân hệ giám sát. **Đề nghị BA mở một mục riêng.**
*(Vị trí: `custom/wujia_franchise/models/wujia_franchise_inspection.py` dòng 1772.)*

### 2. Cửa hàng **HN-02 (Đống Đa)** hiện không có Chủ tiệm còn hiệu lực

Trước khi bật điều kiện "phải có Chủ tiệm mới kích hoạt được cửa hàng", Dev đã **đọc số liệu thật
trên máy chủ thử nghiệm** (chỉ đọc, không sửa gì): ba cửa hàng đều đang hoạt động, đều đã có đối
tác, **riêng HN-02 không có Chủ tiệm nào còn hiệu lực**.

Điều kiện mới **cố ý đặt ở nút bấm chứ không phải ràng buộc dữ liệu**, nên HN-02 vẫn vận hành
bình thường, không bị khoá. Nhưng Dev không biết đây là **dữ liệu thiếu thật** (cần bổ sung Chủ
tiệm) hay chỉ là **dữ liệu dựng để thử** (không cần xử lý).

**Nhờ BA xác nhận.** Nếu là dữ liệu thật thiếu, đề nghị mở một mục riêng để bổ sung Chủ tiệm cho
HN-02 trước khi lên bản chạy thật.

---

## Tóm lại, Dev cần gì

| # | Câu hỏi | Ảnh hưởng nếu chưa trả lời |
|---|---|---|
| a | Thẻ đầu trang Thông tin cửa hàng: khối nào lên trên? | 2 chỗ chưa về khuôn chung |
| b | "2 dòng" hay "không cắt chữ" — bỏ cái nào? | Bảng thành phần còn mâu thuẫn trên giấy |
| c | Ba chỗ tiêu đề mục hay tiêu đề thẻ? | 3 chỗ treo từ đợt trước |
| d | Thẻ bộ lọc có thêm tiêu đề mới không? | Phạm vi issue chưa xác định |
| e | Bốn chỗ hai khối bên phải: chọn ra sao? | 4 chỗ chưa về khuôn chung |
| + | Hai việc đề nghị mở mục riêng | Ngoài phạm vi issue này |

**Không gấp** — mọi chỗ nêu trên đang hiển thị bình thường, không có lỗi nào người dùng đang gặp.
BA trả lời xong thì gỡ `Need Clarification`, Dev làm nốt và issue đóng được 100%.
