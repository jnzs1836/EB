
class Info {

    constructor() {
        this.check_list = Info.get_localStorage("check_list");
    }

    interval_check() {
        setInterval(
            () => this.check_list.map(stock => {
            Info.check_price(stock);
        }), 20000);
    }

    static get_localStorage(name) {
        if (typeof (Storage) !== "undefined")
            return JSON.parse(localStorage.getItem(name)) || [];
        else
            return Cookies.getJSON(name) || [];
    }

    static set_localStorage(name, value) {
        if (typeof (Storage) !== "undefined")
            localStorage.setItem(name, JSON.stringify(value));
        else
            Cookies.set(name, value, { expires: 365 });
    }

    static check_price(stock) {
        fetch('/stock', {
            body: JSON.stringify({code: stock.stock_id}),
            cache: 'no-cache',
            credentials: 'same-origin',
            headers: {
                'content-type': 'application/json'
            },
            method: 'POST',
            redirect: 'follow',
            referrer: 'no-referrer'
        })
            .then(response => response.json())
            .then(res => {
                if(Number(res.stock_price.current_price) * Number(stock.info_type) > Number(stock.stock_price) * Number(stock.info_type)) {
                    this.show_info(stock);
                }
            })
            .catch(err => {
                console.log(err);
            })
    }
    static show_info(stock) {
        $("#infoModalPopovers_stock_id")[0].innerText = stock.stock_id;
        $("#infoModalPopovers_stock_price")[0].innerText = stock.stock_price;
        $("#infoModalPopovers_info_type")[0].innerText = stock.info_type > 0 ? "高于" : "低于";
        $("#infoModalPopovers").modal('show');
    };

    stop_info() {
        let stock_id = $("#infoModalPopovers_stock_id")[0].innerText;
        let stock_price = $("#infoModalPopovers_stock_price")[0].innerText;
        let info_type =  $("#infoModalPopovers_info_type")[0].innerText === "高于" ? 1 : -1;
        this.check_list = this.check_list.filter(x =>
            ! (x.stock_id === stock_id && x.stock_price === stock_price && x.info_type === info_type));
        Info.set_localStorage("check_list", this.check_list);
    }
}