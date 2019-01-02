#coding:utf-8

import os

DEBUG = True

SECRET_KEY = os.urandom(24)

HOSTNAME = '106.12.213.229'
PORT = '3306'
DATABASE = 'web_data'
USERNAME = 'root'
PASSWORD = 'root'
DB_URI = 'mysql+mysqldb://{}:{}/{}?charset=utf8'.format(USERNAME,PASSWORD,HOSTNAME,PORT,DATABASE)
SQLALCHEMY_DATABASE_URI = DB_URI
