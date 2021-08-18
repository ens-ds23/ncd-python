from .read import NCDAccessor
from .util import NCDException
from struct import unpack

class NCDHeader:
    HeaderSize = 28
    Magic = 0x4E00C0FE

    def __init__(self):
        pass

    def read(self, reader: NCDAccessor):
        bytes = reader.read(0,NCDHeader.HeaderSize)
        (magic,version,number_of_pages,heap_size,table_size,stamp) = unpack("<IIQIII",bytes)
        if magic != NCDHeader.Magic:
            raise NCDException("Incorrect magic number")
        if version != 0 and version != 1:
            raise NCDException("Bad version {0}".format(version))
        self.pointer_len = 2 if version == 1 else 4
        self.number_of_pages = number_of_pages
        self.heap_size = heap_size
        self.table_size = table_size
        self.stamp = stamp

    def unpack_format(self) -> int:
        if self.pointer_len == 2:
            return "<H"
        else:
            return "<I"

    def unused(self) -> int:
        if self.pointer_len == 2:
            return 0xFFFF
        else:
            return 0xFFFFFFFF

    def page_size(self) -> int:
        return self.heap_size + self.table_size * self.pointer_len + 4

    def table_start(self) -> int:
        return self.heap_size

    def page_offset(self, index: int) -> int:
        return self.page_size() * index

    def stamp_offset(self, index: int) -> int:
        return self.page_offset(index+1)-4

    def hash_page_index(self, hash: int) -> int:
        if self.table_size == 0:
             return 0
        return (hash//self.table_size) % self.number_of_pages

    def hash_page_slot(self, hash: int) -> int:
        return hash%self.table_size

    def hash_ext(self, hash: int) -> int:
        if self.table_size == 0:
            return 0
        return (hash//self.table_size//self.number_of_pages) & 0xFFFFFFFF
