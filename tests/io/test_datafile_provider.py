from datatools.io.storage import Storage
from datatools.io.datafile_provider import DatafileProvider


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


def test_datafile_provider():
    storage = StorageMock()
    dfp = DatafileProvider(storage)
    assert list(dfp.get_file_names()) == ['file1', 'file2']
