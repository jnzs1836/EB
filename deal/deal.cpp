/*
   ��������
   g++ -fPIC deal.cpp -o libdeal.so -shared
   export CPLUS_INCLUDE_PATH="$CPLUS_INCLUDE_PATH:/home/jnzs1836/anaconda3/include/python3.6m"
   export CPLUS_INCLUDE_PATH="$CPLUS_INCLUDE_PATH:/root/anaconda3/include/python3.6m
*/

#include <time.h>
#include <iostream>
#include<cstdio>
#include <string>
#include <Python.h>

//#define double float
using namespace std;
struct stock{
	int stock_id;
	int order_type;
	char Time[40];
	int user_id;
	int volume;
	double price; 
}__attribute__ ((packed, aligned(1)));

struct exchange{
	int stock_id;
	int buy_id;
	int sell_id;
	char Time[40];
	int volume;
	double price;
}__attribute__ ((packed, aligned(1)));  ;

struct testStructure {
    int a;
    int n;
};
extern "C"
struct testStructure testFunction(testStructure p){
    testStructure k;
    k.a = 10;
    k.n = 3;

    return k;
}
extern "C"
exchange Deal(stock LongOrderStructure, stock ShortOrderStructure, double Limit, double ClosePrice ){
    exchange Result;
//    Result.volume = 2;
//    Result.price = 3;
//    Result.buy_id = 2;
//    Result.Time[0] = '2';
//    Result.sell_id = 3;
//    Result.price = 1.0;
//    exchange get = Result;
//
//    printf("result: %d %f %d\n", Result.volume, Result.price, Result.buy_id);
//    return Result;
    stock *LongOrder = &LongOrderStructure;
    stock *ShortOrder = &ShortOrderStructure;
	double limit_up = ClosePrice + (ClosePrice*Limit);  /*?????????????*/
	double limit_down = ClosePrice - (ClosePrice*Limit);
	double MiddlePrice;   /*?��??*/

	if(LongOrder->price == ShortOrder->price){
        printf("volume cpp %d\n",LongOrder->volume);
	  /*???????*/
		if(LongOrder->price>limit_up||LongOrder->price<limit_down){  /*?????????*/;

			Result.volume=0;
//			printf("Hello World\n");
			return Result;    /*????????????????0????*/
		}
		else{
			Result.stock_id = LongOrder->stock_id;
		    Result.buy_id = LongOrder->user_id;
		    Result.sell_id = ShortOrder->user_id;
		    time_t tmp;
            struct tm *timer = NULL;
            time(&tmp);
            timer = localtime(&tmp);
            strftime(Result.Time,40,"%Y-%m-%d %I:%M:%S",timer);
            Result.price = LongOrder->price;
            if(LongOrder->volume > ShortOrder->volume){  /*?????????????*/
        	    Result.volume = ShortOrder->volume;
        	    LongOrder->volume -= ShortOrder->volume;
        	    ShortOrder->volume = 0;
        	    return Result;
		    }
            else if(LongOrder->volume < ShortOrder->volume){
        	    Result.volume = LongOrder->volume;
        	    ShortOrder->volume -= LongOrder->volume;
        	    LongOrder->volume = 0;
        	    return Result;
		    }
		    else{

			    Result.volume = LongOrder->volume;  /*?????????????????????????????0*/

			    LongOrder->volume = 0;
			    ShortOrder->volume = 0;
			    return Result;
		    }
		}
	}
	else if(LongOrder->price < ShortOrder->price){  /*?????????????????*/
		Result.volume = 0;
		return Result;
	}
	else {    /*?????????*/
		MiddlePrice = (LongOrder->price+ShortOrder->price)/2;
		if(MiddlePrice>limit_up || MiddlePrice<limit_down){ /*?????????*/
			Result.volume = 0;
			return Result;
		}
		else{
			Result.stock_id = LongOrder->stock_id;
		    Result.buy_id = LongOrder->user_id;
		    Result.sell_id = ShortOrder->user_id;
		    time_t tmp;
            struct tm *timer = NULL;
            time(&tmp);
            timer = localtime(&tmp);
            strftime(Result.Time,40,"%Y-%m-%d %I:%M:%S",timer);
            if(ShortOrder->price<limit_down){    /*?????????????*/
            	Result.price = limit_down;
			}
			else if(LongOrder->price>limit_up){  /*?????????????*/
				Result.price = limit_up;
			}
			else
			    Result.price = MiddlePrice;
			if(LongOrder->volume > ShortOrder->volume){  /*??????????????*/
        	    Result.volume = ShortOrder->volume;
        	    LongOrder->volume -= ShortOrder->volume;
        	    ShortOrder->volume = 0;
        	    return Result;
		    }
            else if(LongOrder->volume < ShortOrder->volume){
        	    Result.volume = LongOrder->volume;
        	    ShortOrder->volume -= LongOrder->volume;
        	    LongOrder->volume = 0;
        	    return Result;
		    }
		    else{
			    Result.volume = LongOrder->volume;
			    LongOrder->volume = 0;
			    ShortOrder->volume = 0;
			    return Result;
		    }
		}
	}
}
/*���ݽ���й�Ʊ���Ƿ�Ϊ0�ж��Ƿ��ϳɹ�*/ 
/*������ָ��ṹ�й�Ʊ���Ƿ�Ϊ0�ж��Ƿ���Ҫ�������*/ 
