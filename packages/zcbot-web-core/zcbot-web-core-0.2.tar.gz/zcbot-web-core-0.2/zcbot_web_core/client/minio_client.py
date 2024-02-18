# -*- coding: utf-8 -*-
import os
import typing
from datetime import timedelta
from typing import Optional, Dict
from minio import Minio
from minio.error import NoSuchKey
from ..exception.exceptions import NoConfigException
from ..lib import cfg, logger

LOGGER = logger.get('MinIOClient')


# MinIO客户端简易封装
class MinIO(object):

    def __init__(self,
                 endpoint: str = None,
                 access_key: str = None,
                 secret_key: str = None,
                 region: str = None,
                 tmp_dir: str = None):
        self.endpoint_private = endpoint or cfg.get('MINIO_ENDPOINT_PRIVATE') or cfg.get('MINIO_ENDPOINT_PUBLIC')
        self.endpoint_public = cfg.get('MINIO_ENDPOINT_PUBLIC')
        self.endpoint_public_scheme = cfg.get('MINIO_ENDPOINT_PUBLIC_SCHEME', 'http')
        if not self.endpoint_private:
            raise NoConfigException('MinIO endpoint not config!')
        self.access_key = access_key or cfg.get('MINIO_ACCESS_KEY')
        if not self.access_key:
            raise NoConfigException('MinIO access_key not config!')
        _secret_key = secret_key or cfg.get('MINIO_SECRET_KEY')
        if not _secret_key:
            raise NoConfigException('MinIO secret_key not config!')
        self.region = region or cfg.get('MINIO_REGION') or 'region-default'
        if not self.region:
            raise NoConfigException('MinIO region not config!')
        _secure = cfg.get_bool('MINIO_SECURE') or False
        self.max_presigned_day = cfg.get_int('MINIO_PRESIGNED_DAY') or 7
        self.tmp_dir = tmp_dir or cfg.get_bool('MINIO_TMP_DIR') or '/tmp'
        if not self.tmp_dir:
            raise NoConfigException('MinIO tmp_dir not config!')

        self.client = Minio(
            endpoint=self.endpoint_private,
            access_key=self.access_key,
            secret_key=_secret_key,
            region=self.region,
            secure=_secure
        )

        self.public_client = Minio(
            endpoint=self.endpoint_public,
            access_key=self.access_key,
            secret_key=_secret_key,
            region=self.region,
            secure=_secure
        )

    def put_stream(self, bucket_name: str, object_name: str, image_content: bytes, content_type='application/octet-stream') -> Dict:
        metadata = dict()
        metadata['Content-Type'] = content_type or 'application/octet-stream'
        self.client._do_put_object(bucket_name, object_name, image_content, len(image_content), metadata=metadata)
        return {
            'url': f'{self.endpoint_public_scheme}://{self.endpoint_public}/{bucket_name}/{object_name}',
            'file_path': f'{bucket_name}/{object_name}',
        }

    def put_object(self, bucket_name: str, object_name: str, file: typing.IO, content_type='application/octet-stream') -> Dict:
        self.client.put_object(bucket_name, object_name, file, os.fstat(file.fileno()).st_size, content_type=content_type)

        return {
            'url': f'{self.endpoint_public_scheme}://{self.endpoint_public}/{bucket_name}/{object_name}',
            'file_path': f'{bucket_name}/{object_name}',
        }

    def get_download_url(self, bucket_name: str, object_name: str) -> Optional[str]:
        try:
            result = self.client.stat_object(bucket_name, object_name)
            if result and result.last_modified and result.size:
                url = self.public_client.presigned_get_object(
                    bucket_name=bucket_name,
                    object_name=object_name,
                    expires=timedelta(days=self.max_presigned_day),
                    response_headers={"response-content-type": "application/zip"}
                )
                return url
        except NoSuchKey:
            LOGGER.info(f'包不存在: bucket_name={bucket_name}, object_name={object_name}')
        return None
