from struct import unpack


class Verdata:
    """
        No reason to instantiate.
        Assumed to be working as per C# Ultima SDK but untested.
    """
    FILE = open('files/verdata.mul', 'rb')
    patches = []

    @classmethod
    def load(cls):
        total_patches = unpack('i', cls.FILE.read(4))[0]
        for i in range(total_patches):
            cls.patches.append(Entry5D(*unpack('i'*5, cls.FILE.read(20))))

    @classmethod
    def seek(cls, lookup):
        cls.FILE.Seek(lookup)


class Entry5D:
    def __init__(self, file, index, lookup, length, extra):
        self.file = file
        self.index = index
        self.lookup = lookup
        self.length = length
        self.extra = extra


if len(Verdata.patches) == 0:
    print("Loading Verdata")
    Verdata.load()
