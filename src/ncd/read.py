from struct import iter_unpack, unpack
from typing import Tuple, Union
import mmh3

from .accessor import NCDAccessor
from .bitbash import lesqlite2_read
from .header import NCDHeader
from .util import NCDStampException

def compute_hash(value: bytearray):
    return mmh3.hash64(value)[1] & 0xFFFFFFFFFFFFFFFF

def _parse_entry(heap: bytearray) -> Tuple[bytearray,bytearray]:
    offset = 0
    (key_len,numlen) = lesqlite2_read(heap[offset:])
    offset += numlen
    if key_len == 0:
        # external
        (ext_offset,numlen) = lesqlite2_read(heap[offset:])
        offset += numlen
        (ext_len,numlen) = lesqlite2_read(heap[offset:])
        offset += numlen
        keyhash = unpack("<I",heap[offset:offset+4])[0]
        return (ext_offset,ext_len,keyhash)
    else:
        # internal
        key = heap[offset:offset+key_len-1]
        offset += len(key)
        (value_len,numlen) = lesqlite2_read(heap[offset:])
        offset += numlen
        value = heap[offset:offset+value_len]
        return (key,value)

class NCDPage:
    def __init__(self, accessor: NCDAccessor, header: NCDHeader, index: int):
        bytes = accessor.read(header.page_offset(index),header.page_size())
        self._heap = bytes[0:header.heap_size]
        self._table = []
        unused = header.unused()
        table_start = header.table_start()
        for v in iter_unpack(header.unpack_format(),bytes[table_start:table_start+header.table_size*header.pointer_len]):
            self._table.append(None if unused == v[0] else v[0])
        stamp = unpack("<I",bytes[header.stamp_offset(0):header.stamp_offset(0)+4])[0]
        if stamp != header.stamp:
            raise NCDStampException

    def _get_slot(self, slot: int) -> Union[Tuple[int,int,int],Tuple[bytearray,bytearray],None]:
        offset = self._table[slot]
        if offset == None:
            return None
        return _parse_entry(self._heap[offset:])

class NCDRead:
    def __init__(self, accessor: NCDAccessor):
        self._accessor = accessor
        self._header = NCDHeader()
        self._header.read(self._accessor)

    def _resolve_external(self, offset: int, size: int) -> Tuple[bytearray,bytearray]:
        data = self._accessor.read(offset,size)
        pass

    def _try_get(self, key: bytearray) -> bytearray:
        key_hash = compute_hash(key)
        page_index = self._header.hash_page_index(key_hash)
        page = NCDPage(self._accessor,self._header,page_index)
        page_slot = self._header.hash_page_slot(key_hash)
        first_page_slot = page_slot
        while True:
            heap_value = page._get_slot(page_slot)

            # empty slot is finish
            if heap_value == None:
                return None

            # convert externals
            if len(heap_value) == 3:
                ext_hash = self._header.hash_ext(key_hash)
                if ext_hash == heap_value[2]:
                    heap_value = _parse_entry(self._accessor.read(heap_value[0],heap_value[1]))

            # check for match
            if heap_value[0] == key:
                return heap_value[1]

            # carry on
            page_slot += 1
            page_slot %= self._header.table_size
            if page_slot == first_page_slot:
                return None

    def get(self, key: bytearray) -> bytearray:
        while True:
            try:
                return self._try_get(key)
            except NCDStampException:
                new_header = NCDHeader()
                new_header.read(self._accessor)
                if new_header.stamp == self._header.stamp:
                    raise NCDStampException
                self._header = new_header
