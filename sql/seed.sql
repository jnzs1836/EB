use EB;
-- insert into security_account_coporate_user (username ,
-- password ,
-- registration_number ,
-- business_number ,
-- ID_card ,
-- name,
-- phone ,
-- address ,
-- executor ,
-- executor_ID_card ,
-- executor_phone ,
-- executor_address ,
-- is_enabled ,
-- fund_account)
-- VALUES (B111,111,1111,1111,1111,gd,188888,jjj,111,111,111,111,'Y',B111);

insert into  fund_account_user ( username ,	password ,fund_pwd,
ID_card,
enabled_money,
freezing_money ,is_enabled ,
security_account 	) values ('F1000000','11','111','111',100000,0,'Y','B111');

insert into security_in_account (username, security_number,
security_name ,
amount ,
total_price,
freezing_amount )values ('B111',1000,'130',1000,1000,400);