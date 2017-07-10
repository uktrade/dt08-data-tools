from collections import namedtuple

FileInfoNT = namedtuple('FileInfo', 'name data')


class FileInfo(FileInfoNT):
    """ Stores both the name and data of a file """

    @classmethod
    def from_path(cls, path):
        """ Create FileInfo object from local path """

        with open(path, 'rb') as file:
            return cls(path, file.read())
