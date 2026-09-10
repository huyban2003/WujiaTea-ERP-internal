# Đề nghị mở issue riêng — 4 phép kiểm tự động của cụm D3 đang đỏ sẵn trên nhánh chính

**Nguồn:** phát hiện ở lượt D6b (10/09/2026), truy gốc rễ ở lượt D6d. **Không phải lỗi người
dùng nhìn thấy** — 0 ảnh hưởng giao diện, 0 ảnh hưởng dữ liệu. Đây là việc *bảo trì bộ kiểm tra*.

## 1. Sự việc

Chạy 4 nhóm kiểm tra D3/D4/D5/D6 trên 4 mô đun: **4 failed / 261**. Bốn phép đỏ đều thuộc
`custom/wujia_portal_layout/tests/test_d3_card_header.py` (cụm D3 CardHeader, tháng 8).

Đã **chứng minh chúng đỏ sẵn**, không do cụm D6 gây ra: bỏ toàn bộ thay đổi D6 bằng
`git stash -u` rồi chạy lại đúng lệnh đó ⇒ vẫn **4 failed / 204**, **đúng bốn tên test ấy**.

## 2. Gốc rễ từng phép — cả bốn cùng một bệnh

Cả bốn đều là phép kiểm **đọc thẳng mã nguồn** và **ghim cứng tên lớp/tên vùng của thời D3**.
Các cụm D4 và D5 sau đó đã **cố ý** thay chính những tên đó — nên phép kiểm đỏ, còn sản phẩm đúng.

| # | Phép kiểm | Nó đòi gì | Vì sao nay không còn |
|---:|---|---|---|
| 1 | `test_bootstrap_card_header_wrapper_class_is_kept` | 4 lần chuỗi `card-header wj-card-header--flush` ở màn Chi tiết hỗ trợ | **D4f gỡ hẳn lớp `card` của thư viện Bootstrap khỏi Portal** (89 thẻ → 0). Chuỗi đó không còn tồn tại ⇒ đếm ra 0 |
| 2 | `test_store_name_became_subtitle_not_a_second_heading` | một thẻ `<div class="wujia-mdash-card">` chứa tiêu đề + hàng nhãn | **D4 đưa thẻ này về khuôn thẻ nền dùng chung**: lớp `wujia-mdash-card` nay truyền qua thuộc tính `sc_class` chứ không còn viết thẳng trong thẻ. Card **vẫn còn nguyên**, chỉ là phép tìm theo thẻ không thấy |
| 3 | `test_return_sublabels_keep_their_own_shape` | luật màu viết dưới dạng `.card-body > .wj-card-header.wj-return-sublabel …` | **D4f đổi `.card-body` thành `.wj-surface-card__body`**. Tệp giao diện đã sửa đúng (`portal_return.css:134`); **chỉ biểu thức trong phép kiểm còn ghi tên cũ** |
| 4 | `test_exam_summary_card_keeps_the_rhythm_of_its_neighbour` | luật `.wj-exam-pc-sumlist` phải có `margin-top: 18px` | **D4e2 cố ý XOÁ luật riêng này** để nhịp tiêu đề→nội dung của toàn Portal máy tính hội tụ về **một** con số 12. Phép kiểm vẫn đòi con số 18 của thời trước |

⇒ **Không phép nào tố cáo một lỗi thật.** Cả bốn là *phép kiểm cũ chưa được cập nhật theo quyết
định của cụm sau*.

## 3. Vì sao vẫn nên mở phiếu, dù 0 ảnh hưởng người dùng

Bốn phép này **đỏ vĩnh viễn**. Từ nay mỗi lần chạy kiểm tra, người làm phải nhớ *"bốn cái đỏ đó
là bình thường"* — và đó chính là chỗ một lỗi **thật** của CardHeader sẽ lẩn vào mà không ai để ý.
Bộ kiểm tra chỉ có tác dụng khi số đỏ kỳ vọng là **0**.

## 4. Việc phải làm (ước lượng của Dev)

Sửa **phép kiểm**, không sửa sản phẩm — 4 chỗ trong **một** tệp
`custom/wujia_portal_layout/tests/test_d3_card_header.py`:

1. đổi phép đếm sang lớp thẻ nền hiện hành;
2. tìm card theo thuộc tính `sc_class` thay vì theo tên lớp viết thẳng;
3. đổi `.card-body` → `.wj-surface-card__body` trong biểu thức;
4. đổi con số nhịp 18 → 12, hoặc bỏ hẳn phép kiểm này vì cụm D4e2 đã có phép kiểm nhịp riêng
   rộng hơn (đo nhịp tuyệt đối của toàn Portal máy tính).

**Không** `-u` mô đun nào cho người dùng, **không** đụng dữ liệu, **không** đổi giao diện.
Sau khi sửa, đích là **0 failed** trên cả 4 nhóm kiểm tra D3/D4/D5/D6.

## 5. Đề nghị

Xin BA mở **một phiếu riêng** mức Low (việc nội bộ của Dev, không có mặt trên giao diện), hoặc
cho phép Dev gộp vào **lượt kiểm kê D7** — Dev nghiêng về gộp vào D7, vì cụm D7 vốn đã đụng lại
đúng nhóm thành phần này (`UI-LISTCARD-001`, `UI-BUTTON-001`, `UI-FILTER-001`).
