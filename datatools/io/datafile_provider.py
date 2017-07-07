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
