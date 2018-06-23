create database EB;

create table user(
	user_name varchar(20) primary key,
	user_password varchar(40) not null,
	telephone varchar(15) not null,
	user_type char(1) not null,
	start_time datetime,
	day_left int
);

DELIMITER $
create trigger user_limit before insert
on user for each row
begin
if new.user_type not in ("L", "H")
then signal sqlstate '45000';
end if;
end $
DELIMITER ;

create table login_log(
	user_name varchar(20),
	date datetime not null,
	state char(1) not null,
	foreign key (user_name) references user(user_name)
);

DELIMITER $
create trigger login_log_limit before insert
on login_log for each row
begin
if new.state not in ("S", "F")
then signal sqlstate '45000';
end if;
end $
DELIMITER ;

create table vip_log(
	user_name varchar(20),
	start_time datetime not null,
	duration int not null,
	foreign key (user_name) references user(user_name)
);





create table stock_set(
    stock_id char(10),
    stock_name char(20) not null,
    primary key(stock_id)
);


create table today_stock(
	stock_id char(10),
	stock_name char(20) not null,
	price decimal(5,2) not null,
	date datetime not null,
	foreign key (stock_id) references stock_set(stock_id)
);

create table previous_stock(
	stock_id char(10),
	stock_name char(20) not null,
	start_price decimal(5,2) not null,
	end_price decimal(5,2) not null,
	max_price decimal(5,2) not null,
	min_price decimal(5,2) not null,
	date datetime not null,
	foreign key (stock_id) references stock_set(stock_id)
);


create table notice(
    stock_id char(10),
    stock_notice varchar(10000),
    foreign key (stock_id) references stock_set(stock_id)
);



create table pma5(
    stock_id char(10),
    date datetime not null,
    average_price decimal(5,2) not null,
    foreign key (stock_id) references stock_set(stock_id)
);

create table pma10(
    stock_id char(10),
    date datetime not null,
    average_price decimal(5,2) not null,
    foreign key (stock_id) references stock_set(stock_id)
);


create table pma30(
    stock_id char(10),
    date datetime not null,
    average_price decimal(5,2) not null,
    foreign key (stock_id) references stock_set(stock_id)
);

CREATE TABLE vcode(
telephone VARCHAR(15) NULL,
code CHAR(6) NULL,
`no` INT NOT NULL AUTO_INCREMENT,
PRIMARY KEY (`no`));

create index ts_index on today_stock(date);

create index ps_index on previous_stock(date);

create index p5_index on pma5(date);

create index p10_index on pma10(date);

create index p30_index on pma30(date);




create index ts_si on today_stock(stock_id);

create index ps_si on previous_stock(stock_id);

create index p5_si on pma5(stock_id);

create index p10_si on pma10(stock_id);

create index p30_si on pma30(stock_id);

create index n_si on notice(stock_id);


create database account;
use account
create table fund_account_manager(
username varchar(10),
password varchar(100) not null,
primary key(username)
);
create table security_account_manager(
username varchar(10),
password varchar(100) not null,
primary key(username)
);
create table security_account_personal_user(
username varchar(20),
password varchar(100) not null,
name varchar(20) not null,
sex enum('F','M') not null,
ID_card varchar(20) unique not null,
address varchar(20) not null,
profession varchar(20) not null,
educational_background enum('high_school','college') not null,
company varchar(20) not null,
phone varchar(11) not null,
is_enabled enum('Y','N') not null,
fund_account varchar(20) not null,
primary key(username)
);
create table security_account_coporate_user(
username varchar(20),
password varchar(100) not null,
registration_number varchar(20) not null,
business_number varchar(20) not null,
ID_card varchar(20) unique not null,
name varchar(20) not null,
phone varchar(11) not null,
address varchar(20) not null,
executor varchar(20) not null,
executor_ID_card varchar(20) not null,
executor_phone varchar(20) not null,
executor_address varchar(20) not null,
is_enabled enum('Y','N') not null,
fund_account varchar(20) not null,
primary key(username)
);

create table fund_account_user(
username varchar(20),		#账号
password varchar(100) not null,		#账号的密码
fund_pwd varchar(6) not null,		#交易密码
ID_card  varchar(18) not null,		#身份证
enabled_money decimal(10,2) not null,	#不是可用资金 是总资金
freezing_money decimal(10,2) not null,	#冻结资金
is_enabled enum('Y','N') not null,	#账号是够可用
security_account varchar(20) not null,	#关联的证券账户号码
primary key(username)
);

create table security_in_account(
username varchar(20),		#账号
security_number varchar(6),		#股票的编号
security_name varchar(10),		#股票名称
amount int not null,			#持股数量
total_price decimal(10,2) not null,	#股票的持有成本：sum(每次买入价格*每次买入数量)，如果卖出了就减去卖到的钱？
freezing_amount int,			#冻结的股票数
primary key(username, security_number)
);
insert into security_in_account values("222","222","222",11,150.10,10);


insert into security_in_account values('111','600001','tencent',100,100,50);
create table trade_log (id int unsigned not null primary key AUTO_INCREMENT, stock_id varchar(20), buy_id varchar(20), sell_id varchar(20), price integer, volume integer, create_time timestamp not null default current_timestamp)
