import os
import tempfile

from datatools.io.fileinfo import FileInfo


def test_file_info_create_from_path():

    filename = 'somefile.txt'
    data = b'somedata'
    
    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, filename)
        with open(path, 'wb') as file:
            file.write(data)
        fi = FileInfo.from_path(path)

        assert fi.name == path
        assert fi.data.read() == data
