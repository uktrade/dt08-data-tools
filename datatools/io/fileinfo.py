from collections import namedtuple

FileInfoNT = namedtuple('FileInfo', 'name data')


class FileInfo(FileInfoNT):
    """ Stores both the name and data of a file """

    @classmethod
    def from_path(cls, path):
        """ Create FileInfo object from local path """

        return cls(path, open(path, 'rb'))
