import uuid

from datatools.io import storage


def test_s3_storage():
    bucket = 'input.data.dev.uktrade.io'
    s3_storage = storage.S3Storage(bucket)
    for i in s3_storage.get_file_names():
        print(i)

    test_file_name = 'test-{}.test'.format(uuid.uuid1().hex)
    test_file_data = 'test-data-{}'.format(uuid.uuid1().hex)
    s3_storage.write_file(test_file_name, test_file_data)

    test_file_data_actual = s3_storage.read_file(test_file_name).decode()

    print('test file data: ', test_file_data)
    print('actual file data: ', test_file_data_actual)

    assert test_file_data == test_file_data_actual
