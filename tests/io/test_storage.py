import os
import tempfile
import uuid

import pytest

from datatools.io import storage


@pytest.mark.skipif('AWS_DEFAULT_REGION' not in os.environ,
                    reason='test requires AWS environment')
def test_s3_storage():
    bucket = 'input.data.dev.uktrade.io'
    s3_storage = storage.S3Storage(bucket)
    storage_test(s3_storage)


def test_local_storage():
    with tempfile.TemporaryDirectory() as tmpdirname:
        local_storage = storage.LocalStorage(tmpdirname)
        storage_test(local_storage)


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
