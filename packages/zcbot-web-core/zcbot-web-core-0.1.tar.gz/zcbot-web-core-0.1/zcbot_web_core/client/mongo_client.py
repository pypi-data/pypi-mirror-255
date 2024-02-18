# -*- coding: utf-8 -*-
import pytz
from typing import Dict
from pymongo import MongoClient
from ..exception.exceptions import NoConfigException
from ..lib import cfg, logger

LOGGER = logger.get('MongoClient')


class Mongo(object):
    """
    Mongo基础客户端简易封装
    """

    def __init__(self, mongo_uri=None, mongo_db=None, *args, **kwargs):
        self.mongo_uri = mongo_uri or cfg.get('MONGO_URL')
        self.mongo_db = mongo_db or cfg.get('MONGO_DB')
        if not self.mongo_uri:
            raise NoConfigException('mongodb uri not config!')
        if not self.mongo_db:
            raise NoConfigException('mongodb database not config!')

        self.client = MongoClient(self.mongo_uri, tz_aware=True, tzinfo=pytz.timezone('Asia/Shanghai'))
        self.db = self.client[self.mongo_db]
        LOGGER.info(f'init mongo client: uri={self.mongo_uri}, db={self.mongo_db}')

    # 获取集合
    def get_collection(self, coll):
        return self.db.get_collection(coll)

    # 查询对象
    def get(self, collection, query={}):
        result = self.db[collection].find_one(query)
        return result

    # 统计数量
    def count(self, collection, query={}):
        return self.db[collection].count(query)

    # 查询列表
    def list(self, collection, query={}, fields=None, sort=[]):
        cursor = self.db[collection].find(filter=query, projection=fields, sort=sort)
        return list(cursor)

    # 分页查询
    def page(self, collection, query={}, page_no=1, page_size=20, fields=None, sort=[]):
        total = self.db[collection].count_documents(query) or 0
        cursor = self.db[collection].find(query, fields, sort=sort).skip(page_size * (page_no - 1)).limit(page_size)
        rows = list(cursor) or []

        return rows, total

    # 查询列表前N个
    def top(self, collection, query={}, sort=[], limit=1, fields=None):
        cursor = self.db[collection].find(filter=query, projection=fields, sort=sort, limit=limit)
        rows = list(cursor)
        if limit == 1 and len(rows):
            return rows[0]

        return rows

    # 查询去重列表
    def distinct(self, collection, dist_key, query={}, fields=None):
        return self.db[collection].find(query, fields).distinct(dist_key)

    # 含分页聚合查询
    def aggregate_page(self, collection, pipelines, page_no=1, page_size=20):
        skip = page_size * (page_no - 1)
        if pipelines:
            pipelines.append({'$facet': {'total': [{'$count': 'count'}], 'rows': [{'$skip': skip}, {'$limit': page_size}]}})
            pipelines.append({'$project': {'data': '$rows', 'total': {'$arrayElemAt': ['$total.count', 0]}}})

            rs = list(self.db[collection].aggregate(pipelines, session=None, allowDiskUse=True))
            if rs and 'data' in rs[0] and 'total' in rs[0]:
                return rs[0].get('data'), rs[0].get('total')

        return [], 0

    # 聚合查询
    def aggregate(self, collection, pipelines=[]):
        cursor = self.db[collection].aggregate(pipelines, session=None, allowDiskUse=True)
        return list(cursor)

    # 查询分页列表
    def list_with_page(self, collection, query={}, page_size=10000, fields=None):
        rows = list()
        total = self.db[collection].count(query)
        if total > 0 and page_size > 0:
            total_page = round(len(total) / page_size)
            for page in range(0, total_page):
                if fields:
                    cursor = self.db[collection].find(query, fields).skip(page_size * page).limit(page)
                else:
                    cursor = self.db[collection].find(query).skip(page_size * page).limit(page)
                curr_batch = list(cursor)
                if curr_batch:
                    rows.append(curr_batch)
        return rows

    # 插入或更新
    def insert_or_update(self, collection, data, id_key='_id', upsert=True, multi=False):
        return self.db[collection].update({id_key: data[id_key]}, {'$set': data}, upsert=upsert, multi=multi)

    # 插入或更新
    def insert(self, collection, data):
        return self.db[collection].insert_one(data)

    # 更新
    def update(self, collection, filter, data, multi=False):
        return self.db[collection].update(filter, {'$set': data}, multi=multi)

    # 原生保存方法
    def save(self, collection, filter, save_data: Dict, upsert=True):
        return self.db[collection].update(filter, save_data, upsert=upsert)

    # 以主键更新
    def update_by_pk(self, collection, pk_val, data, upsert=False):
        return self.db[collection].update({'_id': pk_val}, {'$set': data}, multi=False, upsert=upsert)

    # 批量更新
    def batch_update(self, collection, filter, datas, multi=True):
        return self.db[collection].update(filter, datas, multi=multi)

    # 更新
    def delete(self, collection, filter):
        return self.db[collection].delete_many(filter)

    # 插入或更新
    def bulk_write(self, collection, bulk_list):
        if bulk_list:
            return self.db[collection].bulk_write(bulk_list, ordered=False, bypass_document_validation=True)

    # 创建索引
    def create_index(self, collection, fields):
        return self.db[collection].create_index(fields)

    # 关闭链接
    def close(self):
        self.client.close()

    # 销毁关闭链接
    def __del__(self):
        if self.client:
            try:
                self.client.close()
            except Exception as e:
                print(e)
