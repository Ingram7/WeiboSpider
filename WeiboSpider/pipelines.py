# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from pymongo.errors import DuplicateKeyError
from WeiboSpider.items import *
from WeiboSpider.settings import LOCAL_MONGO_HOST, LOCAL_MONGO_PORT, DB_NAME

import re
import time
import datetime

# items中加入时间戳
class TimePipeline():
    def process_item(self, item, spider):
        if isinstance(item, TweetsItem) or isinstance(item, InformationItem) \
                or isinstance(item, RelationshipsItem) or isinstance(item, CommentItem):
            now = time.strftime('%Y-%m-%d %H:%M', time.localtime())
            item['crawled_at'] = now
        return item

# 清洗时间
class WeiboSpiderPipeline():
    def parse_time(self, date):
        if re.match('刚刚', date):
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
        if re.match('\d+分钟前', date):
            minute = re.match('(\d+)', date).group(1)
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - float(minute) * 60))
        if re.match('\d+小时前', date):
            hour = re.match('(\d+)', date).group(1)
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - float(hour) * 60 * 60))
        if re.match('昨天.*', date):
            date = re.match('昨天(.*)', date).group(1).strip()
            date = time.strftime('%Y-%m-%d', time.localtime(time.time() - 24 * 60 * 60)) + ' ' + date
        if re.match('\d{2}月\d{2}日', date):
            now_time = datetime.datetime.now()
            date = date.replace('月', '-').replace('日', '')
            date = str(now_time.year) + '-' + date
        if re.match('今天.*', date):
            date = re.match('今天(.*)', date).group(1).strip()
            date = time.strftime('%Y-%m-%d', time.localtime(time.time())) + ' ' + date


        return date


    def process_item(self, item, spider):
        if isinstance(item, TweetsItem) or isinstance(item, CommentItem):
            if item.get('created_at'):
                item['created_at'] = item['created_at'].strip()
                item['created_at'] = self.parse_time(item.get('created_at'))

        return item



# class MongoDBPipeline(object):
#     def __init__(self):
#         client = pymongo.MongoClient(LOCAL_MONGO_HOST, LOCAL_MONGO_PORT)
#         # 数据库名
#         db = client[DB_NAME]
#         # 数据库的 集合 名
#         self.Information = db["Information"]
#         self.Tweets = db["Tweets"]
#         self.Comments = db["Comments"]
#         self.Relationships = db["Relationships"]
#
#     def process_item(self, item, spider):
#         """ 判断item的类型，并作相应的处理，再入数据库 """
#         if isinstance(item, RelationshipsItem):
#             self.insert_item(self.Relationships, item)
#         elif isinstance(item, TweetsItem):
#             self.insert_item(self.Tweets, item)
#         elif isinstance(item, InformationItem):
#             self.insert_item(self.Information, item)
#         elif isinstance(item, CommentItem):
#             self.insert_item(self.Comments, item)
#         return item
#
#     @staticmethod
#     def insert_item(collection, item):
#         try:
#             collection.insert(dict(item))
#         except DuplicateKeyError:
#             """
#             说明有重复数据
#             """
#             pass

import pymongo


class MongoPipeline(object):
    def __init__(self, local_mongo_host, local_mongo_port, mongo_db):
        self.local_mongo_host = local_mongo_host
        self.local_mongo_port = local_mongo_port
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):

        return cls(
            local_mongo_host=crawler.settings.get('LOCAL_MONGO_HOST'),
            local_mongo_port=crawler.settings.get('LOCAL_MONGO_PORT'),
            mongo_db=crawler.settings.get('DB_NAME')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.local_mongo_host, self.local_mongo_port)
        # 数据库名
        self.db = self.client[self.mongo_db]
        # 以Item中collection命名 的集合  添加index
        self.db[TweetsItem.collection].create_index([('id', pymongo.ASCENDING)])
        self.db[InformationItem.collection].create_index([('id', pymongo.ASCENDING)])
        self.db[RelationshipsItem.collection].create_index([('id', pymongo.ASCENDING)])
        self.db[CommentItem.collection].create_index([('id', pymongo.ASCENDING)])
    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, InformationItem) or isinstance(item, TweetsItem):
            self.db[item.collection].update({'id': item.get('id')},
                                            {'$set': item},
                                            True)
        elif isinstance(item, RelationshipsItem):
            self.db[item.collection].update(
                {'id': item.get('id')},
                {'$addToSet':
                    {
                        'follows': {'$each': item['follows']},
                        'fans': {'$each': item['fans']}
                    }
                },
                True)


        elif isinstance(item, CommentItem):
            self.insert_item(self.db[item.collection], item)

        return item

    @staticmethod
    def insert_item(collection, item):
        try:
            collection.insert(dict(item))
        except DuplicateKeyError:
            """
            说明有重复数据
            """
            pass