from abc import ABCMeta, abstractmethod
from pathlib import Path
import os

import boto3


class Storage(metaclass=ABCMeta):
    """
    An abstraction of a key-value storage medium.

    The keys are called file_name and the key-value pair is referred to as a file.
    Use the read_file method to get the data within the file.
    """

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
        bucket_name = self._strip_scheme(bucket_name)
        dirs = bucket_name.split('/')
        self.bucket_name = dirs[0]
        self._filename_prefix = '/'.join(dirs[1:])

    def _strip_scheme(self, bucket_name):
        if bucket_name.startswith('s3://'):
            return bucket_name[5:]
        return bucket_name
    
    def _get_bucket(self):
        s3 = boto3.resource('s3')
        return s3.Bucket(self.bucket_name)

    def _get_s3_object(self, key):
        s3 = boto3.resource('s3')
        return s3.Object(self.bucket_name, key)

    def _abs_file_name(self, file_name):
        return self._filename_prefix + '/' + file_name

    def _rel_file_name(self, file_name):
        if file_name.startswith(self._filename_prefix):
            return file_name[len(self._filename_prefix)+1:]

    def delete_file(self, file_name):
        abs_fn = self._abs_file_name(file_name)
        
        b = self._get_bucket()
        b.delete_objects(Delete={
            'Objects': [
                {'Key': abs_fn}
            ]
        }
        )

    def write_file(self, file_name, data):
        abs_fn = self._abs_file_name(file_name)
        b = self._get_bucket()
        b.put_object(Key=abs_fn, Body=data)

    def read_file(self, file_name):
        abs_fn = self._abs_file_name(file_name)
        obj = self._get_s3_object(abs_fn)
        return obj.get()['Body'].read().decode()

    def get_file_names(self):
        bucket = self._get_bucket()
        for o in bucket.objects.all():
            yield self._rel_file_name(o.key)

    def create_storage(self, folder_name):
        raise NotImplemented()


class LocalStorage(Storage):

    def __init__(self, base_path):
        self.base_path = base_path
        self._path = Path(base_path)

    def get_file_names(self):
        for p in self._path.glob('**/*'):
            if p.is_file():
                fn = str(p)[len(self.base_path):]
                if fn.startswith(os.path.sep):
                    fn = fn[1:]
                yield fn

    def write_file(self, file_name, data):
        path = self._full_path(file_name)
        with open(path, 'w') as file:
            file.write(data)

    def read_file(self, file_name, binary=False):
        path = self._full_path(file_name)
        mode = 'br' if binary else 'r'
        with open(path, mode) as file:
            return file.read()

    def delete_file(self, file_name):
        path = self._full_path(file_name)
        os.remove(path)

    def create_storage(self, folder_name):
        raise NotImplemented()

    def _full_path(self, file_name):
        return os.path.join(self.base_path, file_name)


class StorageFactory:
    @staticmethod
    def create(url):
        """
        Attempt to create the appropriate storage class intelligently
        """
        if 'AWS_DEFAULT_REGION' in os.environ:
            return S3Storage(url)
        else:
            return LocalStorage(url)
