# -*- coding: utf-8 -*-
from ..lib import cfg, logger

LOGGER = logger.get('RedisClient')


# @singleton(不要加单例,目前项目已经不支持)
class Redis(object):
    """
    Redis客户端简易封装（单例）
    """

    def __init__(self, redis_uri=None, redis_db=None, decode_responses=True):
        import redis

        if not redis_uri:
            redis_uri: str = cfg.get('REDIS_URL') or 'redis://localhost:6379'
        if not redis_db:
            redis_db: str = cfg.get('REDIS_DB')
        self.client = redis.Redis.from_url(url=redis_uri, db=redis_db, decode_responses=decode_responses)
        LOGGER.info(f'init redis client: uri={redis_uri}, db={redis_db}')

    # 关闭链接
    def close(self):
        self.client.close()

    # 销毁关闭连接池
    def __del__(self):
        if self.client:
            try:
                self.client.close()
            except Exception as e:
                print(e)
