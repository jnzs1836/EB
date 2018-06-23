function time() {
    let time_div = document.getElementById('showtime');
    let now = new Date();
    time_div.innerHTML = now.getFullYear()+"年"+(now.getMonth()+1)+"月"+now.getDate()+"日"+now.getHours()+"时"+now.getMinutes()+"分"+now.getSeconds()+"秒";
    setTimeout(time, 1000);
}

function logout() {
    sessionStorage.setItem("log_state", "");
    sessionStorage.setItem("log_security_username", "");
}

function login() {
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;
    if (username.length === 0 || password.length === 0) {
        alert('请输入用户名和密码');
    }
    else {
        info = {'username':username, 'password':password}
        text = JSON.stringify( info );

        var xmlhttp = new XMLHttpRequest();
        xmlhttp.open("POST","/account_user_login", true);
        xmlhttp.setRequestHeader("Content-type", "application/json");
        xmlhttp.send(text);

        xmlhttp.onreadystatechange = function() {
            if (xmlhttp.readyState === 4 && xmlhttp.status === 200) {

                var temp = JSON.parse( xmlhttp.responseText );
                sessionStorage.setItem("log_state", temp.state);
                sessionStorage.setItem("log_security_username", temp.security_username);
                if (sessionStorage.getItem("log_state") === "true") {
                    window.location.href="/index";
                }
                else
                    alert('账号或密码错误！');
            }
        }
    }
}

function  change() {
    var oldpswd = document.getElementById('oldpswd').value;
    var newpswd1 = document.getElementById('newpswd1').value;
    var newpswd2 = document.getElementById('newpswd2').value;

    if (newpswd1 !== newpswd2) {
        alert('输入的新密码不一致！');
    }
    else {
        info  = {'username':sessionStorage.getItem("log_security_username"), 'password':oldpswd, 'new_password':newpswd1};
        text = JSON.stringify( info );

        xmlhttp = new XMLHttpRequest();
        xmlhttp.open("POST", "/change_password", true);
        xmlhttp.setRequestHeader("Content-type", "application/json");
        xmlhttp.send(text);

        xmlhttp.onreadystatechange = function() {
            if (xmlhttp.readyState === 4 && xmlhttp.status === 200) {

                var temp = JSON.parse( xmlhttp.responseText );
                alert( temp.msg );
                if (temp.state == "true")
                    window.location.href="/index";
                else
                    window.location.href="/change_password";
            }
        }
    }
}
