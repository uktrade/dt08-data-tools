import os
import tempfile
import uuid
import zipfile

import pytest
from contextlib import contextmanager

from datatools.io.storage import Storage, LocalStorage
from datatools.io.datafile_provider import DatafileProvider
from datatools.io.storage import LocalStorage, Storage


class StorageMock(Storage):
    def get_file_names(self):
        return 'file1 file2 .DS_Store'.split()

    def write_file(self, file_name, data):
        raise NotImplementedError

    def read_file(self, file_name):
        return 'some data'

    def delete_file(self, file_name):
        raise NotImplementedError

    def create_storage(self, folder_name):
        raise NotImplementedError

    def __str__(self):
        return f'<StorageMock>'

    def get_sub_storage(self):
        raise NotImplementedError


class TestDatafileProvider:

    def test_get_file_name(self):
        storage = StorageMock()
        dfp = DatafileProvider(storage)
        assert list(dfp.get_file_names()) == ['file1', 'file2']

    def test_read_files(self):
        with tmp_zipfile() as tmpdirname:
            # run test
            storage = LocalStorage(tmpdirname)
            dfp = DatafileProvider(storage)
            for name, data in dfp.read_files('test-zipfile.zip', unpack=True):
                assert name == 'some-file.txt'
                assert data.read().decode() == 'test-data'


@contextmanager
def tmp_zipfile():
    with tempfile.TemporaryDirectory() as tmpdirname:
        # create zip file to test extraction
        zf_path = os.path.join(tmpdirname, 'test-zipfile.zip')
        zf = zipfile.ZipFile(zf_path, mode='w')
        zf.writestr('some-file.txt', data='test-data')
        zf.close()
        yield tmpdirname
