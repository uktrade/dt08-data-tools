import datetime
import os
import tempfile
import time
import uuid

import pytest

from datatools.io import storage
from datatools.io.storage import S3Storage


@pytest.mark.skipif('AWS_DEFAULT_REGION' not in os.environ,
                    reason='test requires AWS environment')
class TestS3Storage:
    def test_storage(self):
        bucket = 'input.data.dev.uktrade.io'
        s3_storage = S3Storage(bucket)
        storage_test(s3_storage)

    def test_storage_with_prefix_folder(self):
        bucket = 'input.data.dev.uktrade.io/inputs_tests'
        s3_storage = S3Storage(bucket)
        storage_test(s3_storage)

    def test_strip_storage_scheme(self):
        assert S3Storage('s3://somebucket').bucket_name == \
            S3Storage('somebucket').bucket_name

    def test_sub_storage(self):
        bucket = 'input.data.dev.uktrade.io/inputs_tests'
        storage = S3Storage(bucket)
        storage.write_file('some_sub_folder/some_file', 'some data')
        sub_storage = storage.get_sub_storage('some_sub_folder')
        filenames = list(sub_storage.get_file_names())
        assert 'some_file' in filenames
        # clean up
        sub_storage.delete_file('some_file')

    def test_files_listed_in_order(self):
        """Objects should be retrieved in order"""
        bucket = 'input.data.dev.uktrade.io/inputs_tests'
        storage = S3Storage(bucket)
        storage.write_file('ordered_sub_folder/some_file_4', 'some data 4')
        time.sleep(1)
        storage.write_file('ordered_sub_folder/some_file_2', 'some data 2')
        time.sleep(1)
        storage.write_file('ordered_sub_folder/some_file_3', 'some data 3')
        time.sleep(1)
        storage.write_file('ordered_sub_folder/some_file_1', 'some data 1')
        sub_storage = storage.get_sub_storage('ordered_sub_folder')
        filenames = list(sub_storage.get_file_names())
        assert filenames == ['some_file_4', 'some_file_2', 'some_file_3', 'some_file_1']
        # clean up
        sub_storage.delete_file('some_file_1')
        sub_storage.delete_file('some_file_2')
        sub_storage.delete_file('some_file_3')
        sub_storage.delete_file('some_file_4')


class TestLocalStorage:
    def test_storage(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            local_storage = storage.LocalStorage(tmpdirname)
            storage_test(local_storage)

    def test_does_not_present_subfolders(self):
        """ get_file_names should not return folders, only files
        """
        with tempfile.TemporaryDirectory() as tmpdirname:
            local_storage = storage.LocalStorage(tmpdirname)
            os.makedirs(os.path.join(tmpdirname, 'a_sub_folder'))
            assert len(list(local_storage.get_file_names())) == 0

    def test_sub_storage(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            local_storage = storage.LocalStorage(tmpdirname)
            local_storage.write_file('some_sub_folder/test_file', b'test data')
            sub_storage = local_storage.get_sub_storage('some_sub_folder')
            filenames = list(sub_storage.get_file_names())
            assert 'test_file' in filenames

    def test_sub_storage_right_file_order(self, mocker):
        mocker.patch.object(os.path, 'getmtime', side_effect=_mock_modified_date)
        with tempfile.TemporaryDirectory() as tmpdirname:
            local_storage = storage.LocalStorage(tmpdirname)
            local_storage.write_file('some_sub_folder/2018-01-03_test_file', b'test data 3')
            local_storage.write_file('some_sub_folder/2018-01-02_test_file', b'test data 2')
            local_storage.write_file('some_sub_folder/2018-01-04_test_file', b'test data 4')
            sub_storage = local_storage.get_sub_storage('some_sub_folder')
            filenames = list(sub_storage.get_file_names())
            expected_order = [
                '2018-01-02_test_file',
                '2018-01-03_test_file',
                '2018-01-04_test_file',
            ]
            assert [f == expected_order[i] for i, f in enumerate(filenames)]


def storage_test(storage_instance):
    """ Test an instance of a Storage class """
    test_file_name = 'test-{}.test'.format(uuid.uuid1().hex)
    test_file_data = 'test-data'
    storage_instance.write_file(test_file_name, bytes(test_file_data, 'utf-8'))

    file_names = list(storage_instance.get_file_names())
    assert test_file_name in file_names            # we only assert existence because S3 reuses the storage location

    data = storage_instance.read_file(test_file_name).read()
    data = data if isinstance(data, str) else data.decode()

    assert test_file_data == data

    # clean up
    storage_instance.delete_file(test_file_name)


def _mock_modified_date(path):
    if str(path).endswith('some_sub_folder/2018-01-02_test_file'):
        return datetime.date(2018, 1, 2)
    if str(path).endswith('some_sub_folder/2018-01-03_test_file'):
        return datetime.date(2018, 1, 3)
    if str(path).endswith('some_sub_folder/2018-01-04_test_file'):
        return datetime.date(2018, 1, 4)
