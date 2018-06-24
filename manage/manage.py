from flask import Flask, jsonify, request, render_template
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask_sqlalchemy import SQLAlchemy
import json
import time
import datetime
# from main import db


# from trading.order import change_stock_status, get_buy_sell_items, get_stock_state, set_price_limit

#
# class User(db.Model):
#     __tablename__ = 'admi'
#     user_id = db.Column(db.String(10), primary_key=True)
#     user_password = db.Column(db.String(32))
#     super = db.Column(db.Boolean)
#
#
# class StockState(db.Model):
#     __tablename__ = 'stock_state'
#     stock_id = db.Column(db.String(10), primary_key=True)
#     status = db.Column(db.Boolean)
#     gains = db.Column(db.Float(10, 2))
#     decline = db.Column(db.Float(10, 2))
#
#
# class StockInfo(db.Model):
#     __tablename__ = 'stock_info'
#     stock_id = db.Column(db.String(10), primary_key=True)
#     stock_name = db.Column(db.String(32))
#     newest_price = db.Column(db.Float(10, 2))
#     newest = db.Column(db.Integer)
#
#
# class UserStock(db.Model):
#     __tablename__ = 'user_stock'
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.String(10))
#     stock_id = db.Column(db.String(10))
#
#
# class Buy(db.Model):
#     __tablename__ = 'buy'
#     id = db.Column(db.Integer, primary_key=True)
#     stock_id = db.Column(db.String(10))
#     stock_name = db.Column(db.String(32))
#     price = db.Column(db.Float(10, 2))
#     time = db.Column(db.DateTime)
#     share = db.Column(db.Integer)
#
#
# class Sell(db.Model):
#     __tablename__ = 'sell'
#     id = db.Column(db.Integer, primary_key=True)
#     stock_id = db.Column(db.String(10))
#     stock_name = db.Column(db.String(32))
#     price = db.Column(db.Float(10, 2))
#     time = db.Column(db.DateTime)
#     share = db.Column(db.Integer)
#
#
# class Manager:
#     def __init__(self, app, db):
#         self.app = app
#         self.app.db = db
#
#     def get_token(self, id):
#         config = self.app.config
#         secret_key = config.setdefault('SECRET_KEY')
#         salt = config.setdefault('SECURITY_PASSWORD_SALT')
#         serializer = URLSafeTimedSerializer(secret_key)
#         token = serializer.dumps(id, salt=salt)
#         return token
#
#     def check_token(self, token, max_age=86400):
#         if token is None:
#             return False
#         config = self.app.config
#         secret_key = config.setdefault('SECRET_KEY')
#         salt = config.setdefault('SECURITY_PASSWORD_SALT')
#         serializer = URLSafeTimedSerializer(secret_key)
#         try:
#             id = serializer.loads(token, salt=salt, max_age=max_age)
#         except BadSignature:
#             return False
#         except SignatureExpired:
#             return False
#         user = User.query.filter_by(user_id=id).first()
#         if user is None:
#             return False
#         return True
#
#     def parse_token(self, token, max_age=86400):
#         config = self.app.config
#         secret_key = config.setdefault('SECRET_KEY')
#         salt = config.setdefault('SECURITY_PASSWORD_SALT')
#         serializer = URLSafeTimedSerializer(secret_key)
#         id = serializer.loads(token, salt=salt, max_age=max_age)
#         return id
#
#     def check_password(self, user_id, old_password, new_password="12345678", confirm_password="12345678"):
#         if new_password != confirm_password:
#             return {'result': False, 'msg': 'confirm password fail!', 'code': 1}
#         if len(new_password) > 20 or len(new_password) < 6:
#             return {'result': False, 'msg': 'new password is too long or too short!', 'code': 2}
#         user = User.query.filter_by(user_id=user_id).first()
#         if user is None:
#             return {'result': False, 'msg': 'user doesn\'t exist', 'code': 3}
#         if user.user_password != old_password:
#             return {'result': False, 'msg': 'wrong password', 'code': 4}
#         return {'result': True, 'msg': 'reset successfully'}
#
#     def reset_password(self, user_id, new_password):
#         try:
#             user = User.query.filter_by(user_id=user_id).first()
#             user.user_password = new_password
#             db.session.commit()
#         except:
#             return False
#         return True
#
#     def user_stock_auth(self, user_id, stock_id):
#         user_stock = UserStock.query.filter_by(user_id=user_id, stock_id=stock_id).first()
#         if user_stock is None:
#             return False
#         else:
#             return True
#
#     # def get_stock_info(stock_id):
#     #     stock_info = StockInfo.query.filter_by(stock_id=stock_id).first()
#     #     stock_state = get_stock_state(stock_id)
#     #     if stock_info is None or stock_state is None:
#     #         return {}
#     #     dict = {'stock_id': stock_info.stock_id, 'stock_name': stock_info.stock_name,
#     #             'newest_price': float(stock_info.newest_price), 'newest': float(stock_info.newest),
#     #             'status': stock_state['status'], 'gains': stock_state['gains'], 'decline': stock_state['decline']}
#     #     return dict
#
#     # def change_stock_status(stock_id, status):
#     #     stock_state = StockState.query.filter_by(stock_id=stock_id).first()
#     #     if stock_state is None:
#     #         return False
#     #     try:
#     #         stock_state.status = status
#     #         app.db.session.commit()
#     #     except:
#     #         return False
#     #     return True
#
#     # def set_price_limit(stock_id, price, is_gains):
#     #     # 这里需要一些对price的检查
#     #     stock_state = StockState.query.filter_by(stock_id=stock_id).first()
#     #     if stock_state is None:
#     #         return False
#     #     try:
#     #         if is_gains:
#     #             stock_state.gains = price
#     #         else:
#     #             stock_state.decline = price
#     #         app.db.session.commit()
#     #     except:
#     #         return False
#     #     return True
#
#     # def get_buy_sell_items(stock_id, is_buy):
#     #     try:
#     #         if is_buy:
#     #             slist = Buy.query.filter_by(stock_id=stock_id).all()
#     #         else:
#     #             slist = Sell.query.filter_by(stock_id=stock_id).all()
#     #         return_list = []
#     #         for item in slist:
#     #             item_dict = {
#     #                 'stock_id': item.stock_id,
#     #                 'stock_name': item.stock_name,
#     #                 'price': float(item.price),
#     #                 'time': str(item.time),
#     #                 'share': item.share
#     #             }
#     #             return_list.append(item_dict)
#     #         return return_list
#     #     except Exception as e:
#     #         print(e)
#     #         return []
#
#     def add_authorization(self, user_id, stock_id):
#         try:
#             user = User.query.filter_by(user_id=user_id).first()
#             if user is None:
#                 return {'code': 0, 'msg': 'user does not exist'}
#             stock = StockInfo.query.filter_by(stock_id=stock_id).first()
#             if stock is None:
#                 return {'code': 0, 'msg': 'stock does not exist'}
#             user_stock = UserStock.query.filter_by(user_id=user_id, stock_id=stock_id).first()
#             if user_stock is not None:
#                 return {'code': 0, 'msg': 'authorization exist'}
#             user_stock = UserStock(user_id=user_id, stock_id=stock_id)
#             db.session.add(user_stock)
#             db.session.commit()
#             return {'code': 1, 'msg': 'success'}
#         except Exception as e:
#             print(e)
#             return {'code': 0, 'msg': "error"}
#
#     def delete_authorization(self, user_id, stock_id):
#         try:
#             user = User.query.filter_by(user_id=user_id).first()
#             if user is None:
#                 return {'code': 0, 'msg': 'user does not exist'}
#             stock = StockInfo.query.filter_by(stock_id=stock_id).first()
#             if stock_id is None:
#                 return {'code': 0, 'msg': 'stock does not exist'}
#             user_stock = UserStock.query.filter_by(user_id=user_id, stock_id=stock_id).first()
#             if user_stock is None:
#                 return {'code': 0, 'msg': 'authorization does not exist'}
#             db.session.delete(user_stock)
#             db.session.commit()
#             return {'code': 1, 'msg': 'success'}
#         except Exception as e:
#             print(e)
#             return {'code': 0, 'msg': "error"}
