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


class TestLocalStorage:
    def test_storage(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            local_storage = storage.LocalStorage(tmpdirname)
            storage_test(local_storage)

    def test_does_not_present_subfolders(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            local_storage = storage.LocalStorage(tmpdirname)
            os.makedirs(os.path.join(tmpdirname, 'a_sub_folder'))
            assert len(list(local_storage.get_file_names())) == 0


def storage_test(storage_instance):
    """ Test an instance of a Storage class """
    test_file_name = 'test-{}.test'.format(uuid.uuid1().hex)
    test_file_data = 'test-data-{}'.format(uuid.uuid1().hex)
    storage_instance.write_file(test_file_name, test_file_data)

    file_names = [str(i) for i in storage_instance.get_file_names()]
    assert any(fn.endswith(test_file_name) for fn in file_names)

    test_file_data_actual = storage_instance.read_file(test_file_name)

    assert test_file_data == test_file_data_actual

    # clean up
    storage_instance.delete_file(test_file_name)
