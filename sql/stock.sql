-- -- 交易管理系统的用户
use EB
create table admin_user (
  user_id       varchar(10) not null primary key,
  user_password varchar(32) not null,
  super boolean not null
);
-- 交易管理系统的用户股票权限
create table user_stock (
  id       int auto_increment primary key,
  user_id  varchar(10) not null,
  stock_id varchar(10) not null
);
-- ----------------以下作为测试-----------
-- 不需要
create table stock_state (
  stock_id varchar(10) not null primary key,
  status   boolean,
  gains    float(10, 2),
  decline  float(10, 2)
);
-- 不需要
create table stock_info (
  stock_id     varchar(10) not null primary key,
  stock_name   varchar(32) not null,
  newest_price float(10, 2),
  newest       int unsigned
);
-- 不需要
create table buy (
  id         int auto_increment primary key,
  stock_id   varchar(10)  not null,
  stock_name varchar(32)  not null,
  price      float(10, 2) not null,
  time       timestamp    not null,
  share      int(10) unsigned
);
-- 不需要
create table sell (
  id         int auto_increment primary key,
  stock_id   varchar(10)  not null,
  stock_name varchar(32)  not null,
  price      float(10, 2) not null,
  time       timestamp    not null,
  share      int(10) unsigned
);
-- drop table admin_user;
-- drop table stock_info;
-- drop table stock_state;
-- drop table user_stock;
-- drop table buy;
insert into admin_user values ('max', 'password', TRUE );
insert into admin_user values ('enid', 'password', FALSE );
insert into admin_user values ('user1', 'password', FALSE );
insert into admin_user values ('user2', 'password', FALSE );
insert into admin_user values ('user3', 'password', FALSE );
insert into admin_user values ('user4', 'password', FALSE );
insert into admin_user values ('user5', 'password', FALSE );
insert into admin_user values ('user6', 'password', FALSE );
insert into admin_user values ('user7', 'password', FALSE );
insert into admin_user values ('user8', 'password', FALSE );
insert into admin_user values ('user9', 'password', FALSE );
insert into stock_state values ('101', true, 12.2, 5.5);
insert into stock_state values ('102', false, 32.14, 5.6);
insert into stock_state values ('103', true, 20.2, 10.10);
insert into stock_state values ('104', false, 12.2, 5.0);
insert into stock_info values ('101', 'stock1', 10.11, 100);
insert into stock_info values ('102', 'stock2', 10.22, 100);
insert into stock_info values ('103', 'stock3', 10.33, 100);
insert into stock_info values ('104', 'stock4', 10.33, 100);
insert into user_stock (user_id, stock_id) values ('max', '101');
insert into user_stock (user_id, stock_id) values ('max', '102');
insert into user_stock (user_id, stock_id) values ('max', '103');
insert into user_stock (user_id, stock_id) values ('enid', '101');
insert into user_stock (user_id, stock_id) values ('enid', '104');
-- --
insert into buy (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.11, '2018-01-01 00:00:01', 10);
insert into buy (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.21, '2018-01-02 00:00:01', 10);
insert into buy (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.13, '2018-01-03 00:00:01', 10);
insert into buy (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.41, '2018-01-04 00:00:01', 10);
insert into sell (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.1, '2018-01-01 00:00:01', 10);
insert into sell (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.2, '2018-01-02 00:00:01', 10);
insert into sell (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.3, '2018-01-03 00:00:01', 10);
insert into sell (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-01-04 00:00:01', 10);
insert into sell (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-12 10:00:01', 50);
insert into sell (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-12 11:00:01', 40);
insert into sell (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-12 13:00:01', 30);
insert into sell (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-12 12:07:01', 20);
insert into sell (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:06:01', 20);
insert into sell (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:05:01', 20);
insert into sell (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:04:01', 20);
insert into sell (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:03:01', 20);
insert into sell (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:01:01', 20);
insert into sell (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:08:07', 20);
insert into sell (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:07:06', 20);
insert into sell (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:06:05', 20);
insert into sell (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:05:04', 20);
insert into sell (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:04:03', 20);
insert into sell (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:03:02', 20);
insert into buy (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:06:01', 20);
insert into buy (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:05:01', 20);
insert into buy (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:04:01', 20);
insert into buy (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:03:01', 20);
insert into buy (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:01:01', 20);
insert into buy (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:08:07', 20);
insert into buy (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:07:06', 20);
insert into buy (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:06:05', 20);
insert into buy (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:05:04', 20);
insert into buy (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:04:03', 20);
insert into buy (stock_id, stock_name, price, time, share)
values ('101', 'stock1', 10.4, '2018-06-13 12:03:02', 20);
-- --
insert into stock_state values ('105', true, 12.2, 5.5);
insert into stock_state values ('106', false, 32.14, 5.6);
insert into stock_state values ('107', true, 20.2, 10.10);
insert into stock_state values ('108', false, 12.2, 5.0);
insert into stock_state values ('109', false, 12.2, 5.0);
insert into stock_state values ('110', false, 12.2, 5.0);
insert into stock_state values ('111', false, 12.2, 5.0);
insert into stock_state values ('112', false, 12.2, 5.0);
insert into stock_state values ('113', false, 12.2, 5.0);
insert into stock_state values ('114', false, 12.2, 5.0);
insert into stock_info values ('105', 'stock5', 10.11, 100);
insert into stock_info values ('106', 'stock6', 10.22, 100);
insert into stock_info values ('107', 'stock7', 10.33, 100);
insert into stock_info values ('108', 'stock8', 10.33, 100);
insert into stock_info values ('109', 'stock9', 10.33, 100);
insert into stock_info values ('110', 'stock10', 10.33, 100);
insert into stock_info values ('111', 'stock11', 10.33, 100);
insert into stock_info values ('112', 'stock12', 10.33, 100);
insert into stock_info values ('113', 'stock13', 10.33, 100);
insert into stock_info values ('114', 'stock14', 10.33, 100);
insert into user_stock (user_id, stock_id) values ('max', '105');
insert into user_stock (user_id, stock_id) values ('max', '106');
insert into user_stock (user_id, stock_id) values ('max', '107');
insert into user_stock (user_id, stock_id) values ('max', '108');
insert into user_stock (user_id, stock_id) values ('max', '109');
insert into user_stock (user_id, stock_id) values ('max', '110');
insert into user_stock (user_id, stock_id) values ('max', '111');
insert into user_stock (user_id, stock_id) values ('max', '112');
insert into user_stock (user_id, stock_id) values ('max', '113');
insert into user_stock (user_id, stock_id) values ('max', '114');