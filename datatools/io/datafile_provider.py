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
            if self._should_ignore(fn):
                continue
            yield fn

    def read_files(self, file_name, unpack=False):
        """
        Read the single file or unpack the zip and read those files.

        Returns FileInfo objects (file name, and binary data)
        """
        if file_name.endswith('.zip') and unpack:
            bdata = self.storage.read_file(file_name, binary=True)
            yield from self.read_files_from_zip(bdata)
        else:
            yield FileInfo(file_name, self.storage.read_file(file_name, binary=True))

    @classmethod
    def _should_ignore(cls, filename):
        if filename in cls.ignore_filename_patterns:
            return True
        if filename.startswith('__MACOSX'):
            return True
        return False

    def read_files_all(self, unpack=False):
        for fn in self.get_file_names():
            yield from self.read_files(fn, unpack=unpack)

    @classmethod
    def read_files_from_zip(cls, bdata):
        zf = zipfile.ZipFile(BytesIO(bdata), mode='r')
        members = zf.namelist()
        for m in members:
            if cls._should_ignore(m):
                continue
            yield FileInfo(m, zf.open(m))
