# EB
*软工基股票交易系统*  
*Chen Xin*

操作：
1. 先创建数据库和user
2. add_stock.py中取消add_stocks(stocks)和add_notice(stocks)的注释，并运行
3. 运行kline_control.py
4. 运行stock.control.py
5. 运行main.py 端口为5000
6. 运行mobile.py 端口为1234


## 注
1. 文档结构  
    * EB  
      * static 存放图片、js文件、css文件等  
      * templates 存放html文件  
      * main.py 主函数
      * DB_Connector.py 连接数据库
      * pager.py 分页类
      * config.py 配置文件
      * 等等
