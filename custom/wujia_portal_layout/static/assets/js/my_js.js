$(document).ready(function () {
 
    $("#form_withdraw").on("click", "#request_withdraw", function(){
        var amount = Number( $("#amount_withdraw").val())
        var amount_value = Number( $("#amount-value").val())
        var user_name_login = $("#user_name_login").val()
       
        if (amount == ''){
           Swal.fire(_t('You must enter the amount to continue the transaction'))
        }
        else if (amount < 0){
            Swal.fire(_t('Transaction amount must be greater than 0'))
        }
        else if (amount > amount_value){
            Swal.fire(_t('The amount you want to withdraw exceeds the amount of your wallet'))
        }
        else if (amount != '' && amount > 0){
            Swal.fire({
            title: _t('Confirm sending withdrawal request?'),
            icon: 'info',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33'
            }).then((result) => {
                if (result.isConfirmed) {

                    $.ajax({
                        url: "/bcore/withdraw_action",
                        type: "POST",
                        data: {amount: amount, user_name_login: user_name_login},
                        success: function (data) {
                            Swal.fire(data).then((result)=>{
                                location.reload()
                            }) 
                        }
                    });
                }
            }) 
        }
    })
    $("#button-unsubscribe").on("click", "#button-unsubscribe", function () {
        var order_line_id = $(".order_line_id.active").data("order_line_id")
        console.log('order_line_id = ', order_line_id)
    })
    $("#form-register-investment").on("click", "#register_investment ", function () {
        var price_unit = $("#price_unit").val()
        var product_id = $(".investment_packages_id.active").data("register_investment_id")
        price_unit = parseFloat(price_unit)
        console.log(price_unit)
        let current_balance = $("#current_balance").attr('data-current_balance')
        current_balance = parseFloat(current_balance)
        console.log("current_balance",current_balance)
        if (product_id === undefined) {
            Swal.fire({
                title: _t("Please choose investment package"),
                confirmButtonColor: '#3085d6',
                confirmButtonText: 'OK'
            })
        } else if (Number.isNaN(price_unit)) {
            Swal.fire({
                title: _t("Please enter the investment amount"),
                confirmButtonColor: '#3085d6',
                confirmButtonText: 'OK'
            })
        }else if(price_unit < 15000){
            Swal.fire({
                title: _t("Minimum investment amount 15.000"),
                confirmButtonColor: '#3085d6',
                confirmButtonText: 'OK'
            })
        }else if(price_unit > current_balance || Number.isNaN(current_balance)){
            Swal.fire({
                title: _t("Current Balance not enough"),
                confirmButtonColor: '#3085d6',
                confirmButtonText: 'OK'
            })
        }else{
            $.ajax({
                url: "/bcore/register-investment",
                type: "POST",
                data: {price_unit: price_unit, product_id: product_id},
            }).done(function(ketqua) {
                localStorage.setItem("ORDER_ID",ketqua)
              
                $("#collapseExample").removeClass("hidden");
                $('html, body').animate({
                    scrollTop: $("#collapseExample").offset().top
                }, 1000);
            });
        }
        return false;
    });

    //Begin: [T3352W20] Kết nối fontend Rút tiền ví gốc
    $(".btn-draft-inv").click(function () {
        var draft_id = $(this).attr("value")

        Swal.fire({
            title: _t('Want to withdraw the wallet'),
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'OK'
        }).then((result) => {
            if (result.isConfirmed) {

                $.ajax({
                    url: "/draft-investment/" + draft_id,
                    type: "POST",
                    success: function (data) {
                        Swal.fire(data);
                        location.reload();
                    }
                });
            }
        })
    })
    //End: [T3352W20] Kết nối fontend Rút tiền ví gốc

    // [T3351W20] Kết nối frontend Dừng đầu tư
    $(".btn-stop-inv").click(function () {
        var stop_id = $(this).attr("value")
        console.log('stop_id = ', stop_id)
        Swal.fire({
            title: _t('Are you sure to stop?'),
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33'
        }).then((result) => {
            if (result.isConfirmed) {

                $.ajax({
                    url: "/stop-investment/" + stop_id,
                    type: "POST",
                    success: function (data) {
                        Swal.fire(data).then((result)=>{
                            location.reload()
                        }) 
                    }
                });
            }
        })
    })

    //Tiếp tục đầu tư
    $(".btn-subscribe-inv").click(function () {
        var subscribe_id = $(this).attr("value")
        Swal.fire({
            title: _t('Are you sure to subcrise?'),
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33'
        }).then((result) => {
            if (result.isConfirmed) {

                $.ajax({
                    url: "/subscribe-investment/" + subscribe_id,
                    type: "POST",
                    success: function (data) {
                        Swal.fire(data).then((result)=>{
                            location.reload()
                        });
                    }
                });
            }
        });
    });

//[T3354W20] Kết nối front end Rút tiền ví lãi
    $(".btn-withdraw-money-from-wallet").click(function () {
        var wallet_id = $(this).attr("value")

        Swal.fire({
            title: _t('Want to withdraw profit wallet?'),
            icon: 'info',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'OK'
        }).then((result) => {
            if (result.isConfirmed) {

                $.ajax({
                    url: "/withdraw-money-from-wallet/" + wallet_id,
                    type: "POST",
                    success: function (data) {
                        Swal.fire(data);
                        location.reload();
                    }
                });
            }
        })
    })

    //Begin: [T3353W20] Kết nối frontend Nộp ví gốc
    $(".btn-sale-inv").click(function () {
        var sale_id = $(this).attr("value")

        Swal.fire({
            title: _t('You want to top up the wallet?'),
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'OK'
        }).then((result) => {
            if (result.isConfirmed) {

                $.ajax({
                    url: "/sale-investment/" + sale_id,
                    type: "POST",
                    success: function (data) {
                        Swal.fire(data);
                        location.reload();
                    }
                });
            }
        })
    })

})

//End: [T3353W20] Kết nối frontend Nộp ví gốc

function payment_confirmation() {
    var accept = document.getElementById("accept");
    if(accept.checked==true){
        order_id = localStorage.getItem("ORDER_ID")
        Swal.fire({
            title: _t('Do you want to confirm payment?'),
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'OK'
        }).then(result=>{
           if(result.isConfirmed) {
            $.ajax({
                url: "/bcore/payment_confirmation/",
                data: {order_id: order_id},
                type: "POST",
                success: function (response) {
                    Swal.fire({
                        title: response,
                        confirmButtonColor: '#3085d6',
                        confirmButtonText: 'OK'
                    }).then((result)=>{
                        if(result.isConfirmed){
                            window.location.href="/bcore/fund-management";
                        }
                        $("#collapseExample").addClass("hidden");  
                    })
                }
            });
           }
        })
       
    }else{
        Swal.fire({
            title: _t("Please choose to agree investment terms"),
            confirmButtonColor: '#3085d6',
            confirmButtonText: 'OK'
        })
    }
}
/* Sprint 4.2: defensive — ensure .show-overlay class is never stuck after
   page load. On the production server, JS init ordering with Odoo's
   web.assets_frontend bundle can leave this class active, which causes
   the content-overlay (rgba(0,0,0,0.5)) to cover the sidebar. */
$(document).ready(function () {
    $('.app-content').removeClass('show-overlay');
});
$(window).on('load', function () {
    $('.app-content').removeClass('show-overlay');
});
