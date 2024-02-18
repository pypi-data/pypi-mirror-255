# -*- coding: utf-8 -*-
import pika
from ..exception.exceptions import NoConfigException
from ..lib import cfg, logger

LOGGER = logger.get('RabbitClient')


# RabbitMQ客户端简易封装
class Rabbit(object):

    def __init__(self):
        self.connection_uri = cfg.get('RABBITMQ_URI')
        if not self.connection_uri:
            raise NoConfigException('rabbitmq uri not config!')
        self.connection = pika.BlockingConnection(pika.URLParameters(self.connection_uri))
        LOGGER.info(f'init rabbit client: connection_uri -> {self.connection_uri}')

    def get_channel(self):
        return self.connection.channel()

    def reconnect(self):
        """init a new connection"""
        if self.connection:
            try:
                self.connection.close()
            except Exception as e:
                LOGGER.error(e)

        self.connection = pika.BlockingConnection(pika.URLParameters(self.connection_uri))

    def close(self):
        """close a connection"""
        if self.connection and self.connection.is_open:
            try:
                self.connection.close()
            except Exception as e:
                LOGGER.error(e)
