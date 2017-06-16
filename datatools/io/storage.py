from abc import ABCMeta, abstractmethod
from pathlib import Path
import os

import boto3


class Storage(metaclass=ABCMeta):
    @abstractmethod
    def get_file_names(self):
        ...

    @abstractmethod
    def read_file(self, file_name):
        ...

    @abstractmethod
    def write_file(self, file_name, data):
        ...
        
    @abstractmethod
    def create_storage(self, folder_name):
        ...


class S3Storage(Storage):
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def _get_bucket(self):
        s3 = boto3.resource('s3')
        return s3.Bucket(self.bucket_name)

    def _get_s3_object(self, key):
        s3 = boto3.resource('s3')
        return s3.Object(self.bucket_name, key)

    def write_file(self, file_name, data):
        b = self._get_bucket()
        b.put_object(Key=file_name, Body=data)

    def read_file(self, file_name):
        obj = self._get_s3_object(file_name)
        return obj.get()['Body'].read()

    def get_file_names(self):
        bucket = self._get_bucket()
        for o in bucket.objects.all():
            yield o.key

    def create_storage(self, folder_name):
        raise NotImplemented()
