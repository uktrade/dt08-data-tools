from collections import namedtuple

FileInfoNT = namedtuple('FileInfo', 'name data')


class FileInfo(FileInfoNT):
    """ Stores both the name and data of a file """
