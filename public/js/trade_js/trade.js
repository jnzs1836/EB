global_vars = {
    
}

function render_account_info(data){
    var div = $("#account_info");
    if (data.state == "false"){
        var tmp = `
            <strong>账户信息加载失败，请重试。</strong>
        `;
    }else{
        var tmp =`
        <div style="font-size:20px">
            <span class="glyphicon glyphicon-user"></span>账户资金信息
        </div>
        <table class="table">
            <tr><td><label>可用资金：</label></td><td><strong>{}</strong></td><tr>
            <tr><td><label>冻结资金：</label></td><td><strong>[]</strong></td><tr>
            <tr><td></td><td></td></tr>
        <table>
        <p>资金显示并非实时刷新。</p>
        `.replace("{}", data.fund).replace("[]", data.freeze_fund);
        global_vars.fund = data.fund;
        global_vars.freeze_fund = data.freeze_fund;
    }
    div.html(tmp);
}

function check_trade_form(){
    $.post("/fund_account", {username:get_current_username()}, function(data){
        render_account_info(data);
    })
    //render account info
    $("#trade-form").validate({
        rules:{
            stock_id:{
                required : true
            },
            trade_amount:{
                required:true,
                digits:true,
                min : 1
            },
            stock_price:{
                required : true,
                number : true,
                min : 0.01
            }
        },
        messages:{
            stock_id:{
                required:"股票代码不能为空！"
            },
            trade_amount:{
                required:"交易数量不能为空！",
                digits:"交易数量必须为整数！",
                min:"交易数量不能少于1股！"
            },
            stock_price:{
                required:"交易价格不能为空！",
                number:"交易价格必须用阿拉伯数字表示！",
                min:"交易价格不能低于0.01元！"
            }
        },

    submitHandler:function(form){
        $("#confirm_trade").modal("show");
    }
    });
    // bind form valicdator

    $("#trade_amount").on("input", function(e){
        var price = parseFloat($("#stock_price").val());
        var amount = parseInt($("#trade_amount").val());
        if (isNaN(amount) == false && isNaN(price) == false){
            if(amount * price > global_vars.fund){
                $("#trade_amount").val(Math.floor(global_vars.fund / price));
            } 
        }
    });

    $("#stock_price").on("input", function(e){
        var price = parseFloat($("#stock_price").val());
        var amount = parseInt($("#trade_amount").val());
        if (isNaN(amount) == false && isNaN(price) == false){
            if(amount * price > global_vars.fund){
                $("#stock_price").val(Math.floor(global_vars.fund / amount));
            } 
        }
    });
}

function check_confirm_form(){
    $("#confirm_form").validate({
        rules:{
            fund_psd:{
                required:true
            }
        },
        messages:{
            fund_psd:{
                required:"资金密码输入不能为空！"
            }
        },
        submitHandler:function(form){
            var username = get_current_username();
            send_data = {
                username : username,
                password : $("#fund_psd").val()
            }
            $.post("/account_user_login", send_data, function(data){
                if (data.state == "true"){
                    send_trade($("#trade_form"));
                }
                else{
                    $("#msg_slot").html(create_error_alert("资金密码输入错误！"));
                }
            });
            $("#confirm_trade").modal("hide");
        }
    });
}

function send_trade(form){
    if ($("#sub").val() == "确认买入")
    order_t = 1;
    send_data = {
        stock_id : $("#stock_id").val(),
        volume : $("#trade_amount").val(),
        price: $("#stock_price").val(),
        order_type: order_t
    };
    
    $.post("/trade_shares", send_data, function(data){
        if (data.state == "true"){
            $("#msg_slot").html(create_success_alert(
                "交易指令发布成功!<strong>该笔交易的交易号为：{}</strong>".replace("{}", data.transaction_id)
            ));
            $("#trade-form")[0].reset();
        }
        else{
            $("#msg_slot").html(create_error_alert("交易指令发布失败，请检查输入！"));
        }
    })
}

function create_success_alert(msg){
    var tmp = `
    <div id="myAlert" class="alert alert-success">
        <center>
            <a href="#" class="close" data-dismiss="alert">&times;</a>
            {}
        </center>
    </div>
    `.replace("{}", msg);
    return tmp;
}

function create_error_alert(msg) {
    var tmp = `
    <div id="myAlert" class="alert alert-danger">
        <center>
            <a href="#" class="close" data-dismiss="alert">&times;</a>
            {}
        </center>
    </div>
    `.replace("{}", msg);
    return tmp;
}

function load_transactions(){
    $.get("/all_transaction", function(data){
        if (data.state == "true")
            render_transaction(data);
        else{
            $("#msg_slot").html(create_error_alert(data.message));
        }
    });
}

function create_trade_cell(id, item){
    var tmp = "<div class='trade-cell col-sm-5 text-center'><table class='table' id='{}'>".replace("{}", id);
    var date = new Date(item.timestamp);
    formated_date = date.getFullYear()+"年"+(date.getMonth()+1)+"月"+date.getDate()
        +"日"+date.getHours()+"时"+date.getMinutes()+"分"+date.getSeconds()+"秒";

    tmp += "<tr><td>交易号</td><td>{}</td></tr>".replace("{}", id);
    tmp += "<tr><td>交易时间</td><td>{}</td></tr>".replace("{}", formated_date);
    tmp += "<tr><td>股票代码</td><td>{}</td></tr>".replace("{}", item.stock_id);
    if(item.order_type == 1){
        tmp += "<tr><td>买入价格</td><td>{}</td></tr>".replace("{}", item.price);
        tmp += "<tr><td>买入数量</td><td>{}</td></tr>".replace("{}", item.volume);
    }
    else{
        tmp += "<tr><td>卖出价格</td><td>{}</td></tr>".replace("{}", item.price);
        tmp += "<tr><td>卖出数量</td><td>{}</td></tr>".replace("{}", item.volume);
    }
    tmp += `
    <tr><td></td><td></td></tr>
    </table>
    <div class="cell-button">
        <button class="btn btn-default" name="cancel_tran">
            撤销交易
        </button>
    </div>
</div>
    `;
    return tmp;
}

function render_transaction(data){
    var target = $("#all_transactions");
    for (var key in data.data){
        target.append(create_trade_cell(key, data.data[key]));
    }
    $("[name='cancel_tran']").each(function(){
        $(this).click(function(){
            cancel_transaction($(this).parent().prev().attr("id"));
        });
    });
}

function cancel_transaction(id){
    global_vars.transaction_id = id;
    $("#confirm_cancel").modal("show");
}

function send_cancel(){
    var send_data = {
        transaction_id : global_vars.transaction_id,
        order_type : 2
        //2 means cancel
    }
    $.post("/transaction_state", send_data, function(data){
        if (data.state == "false"){
            $("#msg_slot").html(create_error_alert(data.msg));
        }else{
            $("#msg_slot").html(create_success_alert("交易撤销成功！"));
            reload_transactions();
        }
    });
}

function reload_transactions(){
    $("#all_transactions").html("");
    load_transactions();
}

function check_confirm_cancel(){
    $("#confirm_form").validate({
        rules:{
            fund_psd:{
                required:true
            }
        },
        messages:{
            fund_psd:{
                required:"资金密码输入不能为空！"
            }
        },
        submitHandler:function(form){
            var username = get_current_username();
            send_data = {
                username : username,
                password : $("#fund_psd").val()
            }
            $.post("/account_user_login", send_data, function(data){
                if (data.state == "true"){
                   send_cancel();
                }
                else{
                    $("#msg_slot").html(create_error_alert("资金密码输入错误！"));
                }
            });
            $("#confirm_cancel").modal("hide");
        }
    });
}