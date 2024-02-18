# -*- coding: utf-8 -*-
from ..lib import cfg, logger
from ..exception.exceptions import NoConfigException

LOGGER = logger.get('CeleryClient')


class ZcbotCelery(object):

    @staticmethod
    def init(celery_broker_url: str = None, celery_result_backend: str = None, monitor_redis_uri: str = None, app_code: str = None, monitor_on: bool = True):
        """
        初始化，全局调用一次
        :param celery_broker_url:
        :param celery_result_backend:
        :param monitor_redis_uri:
        :param app_code:
        :param monitor_on:
        :return:
        """
        from zcbot_celery_sdk.client import CeleryClientHolder
        from zcbot_celery_sdk.monitor import CeleryRedisResultMonitor

        _celery_broker_url = celery_broker_url or cfg.get('CELERY_BROKER')
        _celery_result_backend = celery_result_backend or cfg.get('CELERY_BACKEND')
        _monitor_redis_uri = monitor_redis_uri or cfg.get('CELERY_MONITOR_REDIS_URI')
        _app_code = app_code or cfg.get('APP_CODE')
        if not _celery_broker_url:
            raise NoConfigException('Celery broker_url not config!')
        if not _celery_result_backend:
            raise NoConfigException('Celery result_backend not config!')
        if not _monitor_redis_uri:
            raise NoConfigException('Celery monitor_redis_uri not config!')
        if not _app_code:
            raise NoConfigException('Celery app_code not config!')

        # 全局初始化一个默认client实例
        CeleryClientHolder.init_default_instance(
            celery_broker_url=_celery_broker_url,
            celery_result_backend=_celery_result_backend,
            monitor_redis_uri=_monitor_redis_uri,
            app_code=_app_code
        )
        LOGGER.info(f'init zcbot celery client: broker={_celery_broker_url}, backend={_celery_result_backend}, monitor_redis={_monitor_redis_uri}')

        if monitor_on:
            # 结果监听器（异步调用时需要）
            _monitor = CeleryRedisResultMonitor(
                celery_broker_url=_celery_broker_url,
                celery_result_backend=_celery_result_backend,
                monitor_redis_uri=_monitor_redis_uri,
                app_code=_app_code
            )
            _monitor.start()
            LOGGER.info(f'init zcbot celery monitor: broker={_celery_broker_url}, backend={_celery_result_backend}, monitor_redis={_monitor_redis_uri}')
