from collections import namedtuple
from io import BytesIO
import zipfile


FileInfo = namedtuple('FileInfo', 'name data')


class DatafileProvider:
    ignore_filename_patterns = [
        '.DS_Store',
        '.gitignore',
        '__MACOSX',
        'datafile_register.csv'
    ]

    def __init__(self, storage):
        self.storage = storage

    def get_file_names(self):
        for fn in self.storage.get_file_names():
            if fn in self.ignore_filename_patterns:
                continue
            yield fn

    def read_files(self, file_name):
        """
        Read the single file or unpack the zip and read those files.

        Returns FileInfo objects (file name, and binary data)
        """
        if file_name.endswith('.zip'):
            data = self.storage.read_file(file_name, binary=True)
            zf = zipfile.ZipFile(BytesIO(data), mode='r')
            members = zf.namelist()
            for m in members:
                if m in self.ignore_filename_patterns:
                    continue
                yield FileInfo(m, zf.open(m))
        else:
            yield FileInfo(file_name, self.storage.read_file(file_name, binary=True))

    def read_files_all(self):
        for fn in self.get_file_names():
            yield from self.read_files(fn)

