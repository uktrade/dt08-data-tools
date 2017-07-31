import os
import tempfile
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
            local_storage.write_file('some_sub_folder/test_file', 'test data')
            sub_storage = local_storage.get_sub_storage('some_sub_folder')
            filenames = list(sub_storage.get_file_names())
            assert 'test_file' in filenames


def storage_test(storage_instance):
    """ Test an instance of a Storage class """
    test_file_name = 'test-{}.test'.format(uuid.uuid1().hex)
    test_file_data = 'test-data-{}'.format(uuid.uuid1().hex)
    storage_instance.write_file(test_file_name, test_file_data)

    file_names = list(storage_instance.get_file_names())
    assert test_file_name in file_names            # we only assert existence because S3 reuses the storage location

    test_file_data_actual = storage_instance.read_file(test_file_name)

    assert test_file_data == test_file_data_actual

    # clean up
    storage_instance.delete_file(test_file_name)
