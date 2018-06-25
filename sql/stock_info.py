import pymysql

def add_table_1(stocks):
    # 打开数据库连接
    dbForOwner = pymysql.connect(user="root",
                                 password="Aa27268910",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')

    flag = 0
    sql = "insert into stock_state values(%s, %s, %s, %s, %s)"
    args_list = []
    for i in stocks:
        args = []
        args.append(i)
        # args.append()   status
        # args.append()   gains
        # args.append()   decline
        # args.append()   close_price
        args_list.append(args)

    cur = dbForOwner.cursor()

    try:
        for i in args_list:
            cur.execute(sql, i)
        dbForOwner.commit()
        flag = 1

    except Exception as e:
        flag = 0

    finally:
        dbForOwner.close()
        return flag

def add_table_2(stocks):
    # 打开数据库连接
    dbForOwner = pymysql.connect(user="owner",
                                 password="123456",
                                 db="EB",
                                 host="localhost",
                                 charset='utf8mb4')

    flag = 0
    sql = "insert into stock_info values(%s, %s, %s, %s)"
    args_list = []
    for i in stocks:
        args = []
        args.append(i)
        args.append(stocks[i])
        # args.append()   newest_price
        # args.append()   newest
        args_list.append(args)

    cur = dbForOwner.cursor()

    try:
        for i in args_list:
            cur.execute(sql, i)
        dbForOwner.commit()
        flag = 1

    except Exception as e:
        flag = 0

    finally:
        dbForOwner.close()
        return flag


if __name__ == "__main__":
    stocks = {}  # id: name
    for i in range(40):
        stocks[i+100] = "s" + str(i)

    add_table_1(stocks)
    add_table_2(stocks)




