import os
from struct import unpack
from .verdata import Verdata


class FileIndex:
    """
        - No current UOP support.
        - Patches not tested.
        - Output unconfirmed to be accurate.
        - Seek method not implemented
        - Valid() method not implemented
        - Should be refactored -- files can be non existent.
    """
    def __init__(self, idx_filename, mul_filename, length, file_idx):
        try:
            index_file = open(os.path.join('files/', idx_filename), 'rb')
            mul_file = open(os.path.join('files/', mul_filename), 'rb')
        except FileNotFoundError:
            print(f"No file for index {idx_filename if not index_file else mul_filename}")
            return
        idx_file_bytes = len(index_file.read())
        index_file.seek(0)
        count = int(idx_file_bytes / 12)
        self.index_length = idx_file_bytes
        self.stream = mul_file
        self.index = []
        for i in range(count):
            self.index.append(Entry3D(*unpack('i'*3, index_file.read(4*3))))
        for i in range(count, length):
            self.index.append(Entry3D(-1, -1, -1))
        patches = Verdata.patches
        if file_idx > -1:
            for idx, patch in enumerate(patches):
                if patch.file == file_idx and 0 < patch.index < length:
                    self.index[patch.index].lookup = patch.lookup
                    self.index[patch.index].length = patch.length | (1 << 31)
                    self.index[patch.index].extra = patch.extra

    def seek(self, index, is_validation=False):
        null_return = None, 0, 0, False
        if index >= len(self.index) or index < 0:
            return null_return
        entry = self.index[index]
        if entry.lookup < 0 or entry.length < 0:
            return null_return

        length = entry.length & 0x7FFFFFFF
        extra = entry.extra
        patched = False

        if (entry.length & (1 << 31)) != 0:
            patched = True
            stream = Verdata.FILE
            stream.seek(entry.lookup)
            return stream, length, extra, patched

        stream = self.stream
        if not self.stream:# or self.index_length < entry.lookup:
            return null_return
        if not is_validation:
            stream.seek(entry.lookup)
        return stream, length, extra, patched

    def valid(self, index):
        stream, length, extra, patched = self.seek(index, is_validation=True)
        return stream is not None, length, extra, patched


class Entry3D:
    def __init__(self, lookup, length, extra):
        self.lookup = lookup
        self.length = length
        self.extra = extra
