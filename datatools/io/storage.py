from abc import ABCMeta, abstractmethod
from pathlib import Path
import os

import boto3


class Storage(metaclass=ABCMeta):
    @abstractmethod
    def get_file_names(self):
        ...

    @abstractmethod
    def write_file(self, file_name, data):
        ...

    @abstractmethod
    def read_file(self, file_name):
        ...

    @abstractmethod
    def delete_file(self, file_name):
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

    def delete_file(self, file_name):
        b = self._get_bucket()
        b.delete_objects(Delete={
            'Objects': [
                {'Key': file_name}
            ]
        }
        )

    def write_file(self, file_name, data):
        b = self._get_bucket()
        b.put_object(Key=file_name, Body=data)

    def read_file(self, file_name):
        obj = self._get_s3_object(file_name)
        return obj.get()['Body'].read().decode()

    def get_file_names(self):
        bucket = self._get_bucket()
        for o in bucket.objects.all():
            yield o.key

    def create_storage(self, folder_name):
        raise NotImplemented()


class LocalStorage(Storage):

    def __init__(self, base_path):
        self.base_path = base_path
        self._path = Path(base_path)

    def get_file_names(self):
        yield from self._path.glob('**/*')

    def write_file(self, file_name, data):
        path = self._full_path(file_name)
        with open(path, 'w') as file:
            file.write(data)

    def read_file(self, file_name):
        path = self._full_path(file_name)
        with open(path) as file:
            return file.read()

    def delete_file(self, file_name):
        path = self._full_path(file_name)
        os.remove(path)

    def create_storage(self, folder_name):
        raise NotImplemented()

    def _full_path(self, file_name):
        return os.path.join(self.base_path, file_name)
