import io
import os
from abc import ABCMeta, abstractmethod
from pathlib import Path

import boto3


class Storage(metaclass=ABCMeta):
    """
    An abstraction of a key-value storage medium.

    The keys are called file_name and the key-value pair is referred to as a file.
    Use the read_file method to get the data within the file.
    """

    @abstractmethod
    def __str__(self):
        ...

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

    @abstractmethod
    def get_sub_storage(self, sub_folder):
        ...


class S3Storage(Storage):
    def __init__(self, bucket_name, aws_access_key_id=None, aws_secret_access_key=None, profile_name=None):
        bucket_name = self._strip_scheme(bucket_name)
        dirs = bucket_name.split('/')
        self.bucket_name = dirs[0]
        self._filename_prefix = '/'.join(dirs[1:])
        self.profile_name = profile_name
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.session = boto3.session.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            profile_name=profile_name
        )

    def __str__(self):
        return f'<io.storage.S3Storage:{self.bucket_name}/{self._filename_prefix}>'

    def _strip_scheme(self, bucket_name):
        if bucket_name.startswith('s3://'):
            return bucket_name[5:]
        return bucket_name

    def _get_bucket(self):
        s3 = self.session.resource('s3')
        return s3.Bucket(self.bucket_name)

    def _get_s3_object(self, key):
        s3 = self.session.resource('s3')
        return s3.Object(self.bucket_name, key)

    def _abs_file_name(self, file_name):
        return self._filename_prefix + '/' + file_name

    def _rel_file_name(self, file_name):
        if file_name.startswith(self._filename_prefix):
            return file_name[len(self._filename_prefix)+1:]
        return None

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
        b.put_object(Key=abs_fn, Body=data, ServerSideEncryption='AES256')

    def read_file(self, file_name):
        abs_fn = self._abs_file_name(file_name)
        obj = self._get_s3_object(abs_fn)
        bytes_io = io.BytesIO()
        obj.download_fileobj(bytes_io)
        bytes_io.seek(0)
        return bytes_io

    def get_file_names(self):
        bucket = self._get_bucket()
        substorage_objs = [(self._rel_file_name(o.key), o) for o in bucket.objects.all() if self._rel_file_name(o.key)]
        for fn, _ in sorted(substorage_objs, key=lambda o: o[1].last_modified):
            yield fn
    
    def create_storage(self, folder_name):
        raise NotImplemented()

    def _strip_path_separators(self, path):
        return path.strip('/')

    def get_sub_storage(self, sub_folder):
        sub_folder = self._strip_path_separators(sub_folder)
        sub_storage_path = f'{self.bucket_name}/{self._filename_prefix}/{sub_folder}'
        return self.__class__(
            sub_storage_path,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            profile_name=self.profile_name
        )


class LocalStorage(Storage):

    def __init__(self, base_path):
        """
        Args:
            base_path: PosixPath or string
        """
        self.base_path = str(base_path)
        self._path = Path(base_path)

    def __str__(self):
        return f'<io.storage.LocalStorage:{self.base_path}>'

    def get_file_names(self):
        for p in self._path.glob('**/*'):
            if p.is_file():
                fn = str(p)[len(self.base_path):]
                if fn.startswith(os.path.sep):
                    fn = fn[1:]
                yield fn

    def write_file(self, file_name, data):
        path = self._full_path(file_name)
        dir_name = os.path.dirname(path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        with open(path, 'wb') as file:
            file.write(data)

    def read_file(self, file_name):
        path = self._full_path(file_name)
        return open(path, 'br')

    def delete_file(self, file_name):
        path = self._full_path(file_name)
        os.remove(path)

    def create_storage(self, folder_name):
        raise NotImplemented()

    def _full_path(self, file_name):
        return os.path.join(self.base_path, file_name)

    def get_sub_storage(self, sub_folder):
        path = self._path.joinpath(sub_folder)
        return self.__class__(path)


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
