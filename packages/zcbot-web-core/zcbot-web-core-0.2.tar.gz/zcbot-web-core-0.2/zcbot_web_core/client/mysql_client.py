# -*- coding: utf-8 -*-
import pymysql
from pymysql.cursors import DictCursor
from ..lib import cfg, logger

LOGGER = logger.get('MySQLClient')


class MySQL(object):
    """
    MySQL客户端简易封装
    """

    def __init__(self, mysql_host=None, mysql_port=None, mysql_user=None, mysql_password=None, mysql_db=None):
        self._biz_inited = True
        self.host = mysql_host or cfg.get('MYSQL_HOST')
        self.port = mysql_port or cfg.get('MYSQL_PORT')
        self.user = mysql_user or cfg.get('MYSQL_USER')
        self.pwd = mysql_password or cfg.get('MYSQL_PASSWORD')
        self.db = mysql_db or cfg.get('MYSQL_DB')
        self.connection = pymysql.connect(host=self.host, port=int(self.port), user=self.user, password=self.pwd, db=self.db)

    # 查询对象
    def get(self, sql, cursor_type=DictCursor):
        try:
            if self.connection and sql:
                with self.connection.cursor(cursor_type) as cursor:
                    cursor.execute(sql)
                    rs = cursor.fetchone()
                    return rs
            return {}
        except Exception as e:
            print(e)

    # 查询列表
    def list(self, sql, cursor_type=DictCursor):
        try:
            if self.connection and sql:
                with self.connection.cursor(cursor_type) as cursor:
                    cursor.execute(sql)
                    rs_list = cursor.fetchall()
                    return rs_list
            return list()
        except Exception as e:
            print(e)

    # 销毁关闭链接
    def __del__(self):
        if self.connection:
            try:
                self.connection.close()
            except Exception as e:
                print(e)
