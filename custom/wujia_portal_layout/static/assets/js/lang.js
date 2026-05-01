function getCookie(name) {
    // Split cookie string and get all individual name=value pairs in an array
    var cookieArr = document.cookie.split(";");
    
    // Loop through the array elements
    for(var i = 0; i < cookieArr.length; i++) {
        var cookiePair = cookieArr[i].split("=");
        
        /* Removing whitespace at the beginning of the cookie name
        and compare it with the given string */
        if(name == cookiePair[0].trim()) {
            // Decode the cookie value and return
            return decodeURIComponent(cookiePair[1]);
        }
    }
    
    // Return null if not found
    return null;
}

var lang_en ={
    'You have not selected a bank account':'You have not selected a bank account',
    'You have not selected a payment wallet':'You have not selected a payment wallet',
    'You must enter the amount to continue the transaction':'You must enter the amount to continue the transaction',
    'Transaction amount must be greater than 0':'Transaction amount must be greater than 0',
    'The amount you want to withdraw exceeds the amount of your wallet':'The amount you want to withdraw exceeds the amount of your wallet',
    'Confirm sending withdrawal request?':'Confirm sending withdrawal request?',
    'Please enter the investment amount':'Please enter the investment amount',
    'Minimum investment amount 15.000':'Minimum investment amount 15.000 USD',
    'Please choose investment package':'Please choose investment package',
    'Are you sure to stop?':'Are you sure to stop?',
    'Want to withdraw profit wallet?':'Want to withdraw profit wallet?',
    'You want to top up the wallet':'You want to top up the wallet',
    'Want to withdraw the wallet?':'Want to withdraw the wallet?',
    'Do you want to confirm payment?':'Do you want to confirm payment?',
    'Please choose to agree investment terms':'Please choose to agree investment terms',
    'Can not enter negative numbers':'Can not enter negative numbers',
    'Minimum investment is 15,000':'Minimum investment is 15,000 USD',
    'Current Balance not enough':'Current Balance not enough',
    'Overview investment package':'Overview investment packages',
    'Net Profit':'Net Profit',
    'Revenue':'Revenue'
}   
var lang_vi ={
    'You have not selected a bank account':'Bạn chưa chọn tài khoản ngân hàng',
    'You have not selected a payment wallet':'Bạn chưa chọn ví thanh toán',
    'You must enter the amount to continue the transaction':'Bạn phải nhập số tiền để tiếp tục giao dịch',
    'Transaction amount must be greater than 0':'Số tiền giao dịch phải lớn hơn 0',
    'The amount you want to withdraw exceeds the amount of your wallet':'Số dư ví không đủ',
    'Confirm sending withdrawal request?':'Xác nhận gửi yêu cầu rút tiền?',
    'Minimum investment amount 15000':'Số tiền đầu tư tối thiểu 15,000 USD',
    'Please choose investment package':'Xin vui lòng chọn gói đầu tư',
    'Are you sure to stop?':'Bạn có chắc chắn dừng ?',
    'Want to withdraw profit wallet?':'Bạn muốn rút ví lãi?',
    'You want to top up the wallet':'Bạn muốn nạp tiền vào ví gốc',
    'Want to withdraw the wallet?':'Bạn muốn rút ví gốc?',
    'Do you want to confirm payment?':'Bạn có muốn xác nhận thanh toán?',
    'Please choose to agree investment terms':'xin vui lòng chọn đồng ý điều khoản đầu tư',
    'Can not enter negative numbers':'Không thể nhập số âm',
    'Minimum investment amount 15.000':'Đầu tư tối thiểu là 15.000 USD' ,
    'Please enter the investment amount':'Xin vui lòng nhập số tiền đầu tư',
    'Current Balance not enough':'Số dư hiện tại không đủ',
    'Overview investment package':'Tổng quan gói đầu tư',
    'Net Profit':'Lợi nhuận ròng',
    'Revenue':'Doanh thu'
}


var frontend_lang = getCookie("frontend_lang")
console.log( frontend_lang)
function _t(key){
    if(frontend_lang === 'vi_VN'){
        return lang_vi[key];
    }else{
        return lang_en[key];
    }
}