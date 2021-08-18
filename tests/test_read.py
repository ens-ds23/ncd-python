import pathlib
import os.path

from ncd.accessor import NCDBytesReader, NCDFileAccessor
from ncd.read import NCDPage, NCDRead
from ncd.util import NCDException, NCDStampException

def test_reader():
    test_file = os.path.join(pathlib.Path(__file__).parent.resolve(),"smoke.ncd")
    with open(test_file,"rb") as f:
        smoke_data = f.read()
    file_reader = NCDFileAccessor(test_file)
    for offset in (0,1,5,10,15):
        for length in (0,1,7,10):
            got = file_reader.read(offset,length)
            assert got == smoke_data[offset:offset+length]

def test_read_smoke():
    test_file = os.path.join(pathlib.Path(__file__).parent.resolve(),"smoke.ncd")
    reader = NCDRead(NCDFileAccessor(test_file))

def test_bad_magic_version():
    for pos in (0,4):
        for fiddle in (False,True):
            test_file = os.path.join(pathlib.Path(__file__).parent.resolve(),"smoke.ncd")
            with open(test_file,"rb") as f:
                smoke_data = bytearray(f.read())
            if fiddle:
                smoke_data[pos] = 0x21
            try:
                reader = NCDRead(NCDBytesReader(smoke_data))
                assert not fiddle
            except NCDException as e:
                assert fiddle
                assert ("magic" if pos == 0 else "version") in str(e)

def test_header():
    test_file = os.path.join(pathlib.Path(__file__).parent.resolve(),"smoke.ncd")
    with open(test_file,"rb") as f:
        smoke_data = bytearray(f.read())
    reader = NCDRead(NCDBytesReader(smoke_data))
    assert reader._header.number_of_pages == 1
    assert reader._header.heap_size == 0x40
    assert reader._header.table_size == 4
    assert reader._header.stamp == 0x58585858

# reader -> source XXX
def test_page():
    test_file = os.path.join(pathlib.Path(__file__).parent.resolve(),"smoke.ncd")
    with open(test_file,"rb") as f:
        smoke_data = bytearray(f.read())
    read = NCDRead(NCDBytesReader(smoke_data))
    page = NCDPage(read._accessor,read._header,0)
    assert [40,28,57,None] == page._table

def test_page_stamp():
    for tinker_header in [False,True]:
        for tinker_page in [False,True]:
            test_file = os.path.join(pathlib.Path(__file__).parent.resolve(),"smoke.ncd")
            with open(test_file,"rb") as f:
                smoke_data = bytearray(f.read())
            if tinker_header:
                smoke_data[24] = 0x21
            if tinker_page:
                smoke_data[80] = 0x21
            try:
                read = NCDRead(NCDBytesReader(smoke_data))
                _page = NCDPage(read._accessor,read._header,0)
                assert tinker_header == tinker_page
            except NCDStampException:
                assert tinker_header != tinker_page

def test_get_slot():
    test_file = os.path.join(pathlib.Path(__file__).parent.resolve(),"smoke.ncd")
    with open(test_file,"rb") as f:
        smoke_data = bytearray(f.read())
    read = NCDRead(NCDBytesReader(smoke_data))
    page = NCDPage(read._accessor,read._header,0)
    assert page._get_slot(1) == (b"Hello",b"World")
    assert page._get_slot(0) == (84,13,3902212404)
    assert page._get_slot(3) == None

def test_read():
    test_file = os.path.join(pathlib.Path(__file__).parent.resolve(),"smoke.ncd")
    with open(test_file,"rb") as f:
        smoke_data = bytearray(f.read())
    read = NCDRead(NCDBytesReader(smoke_data))
    assert b"World" == read.get(b"Hello")
    assert b"Mars" == read.get(b"Goodbye")
    assert b"f" == read.get(b"e")
    assert None == read.get(b"a")

def check_read_stamp(update_header: bool, update_page: bool, success: bool):
    test_file = os.path.join(pathlib.Path(__file__).parent.resolve(),"smoke.ncd")
    with open(test_file,"rb") as f:
        smoke_data = bytearray(f.read())
    reader = NCDBytesReader(smoke_data)
    read = NCDRead(reader)
    if update_header:
        reader.bytes[24] = 0x21
    if update_page:
        reader.bytes[80] = 0x21
    try:
        read.get(b"Hello")
        assert success
    except NCDStampException:
        assert not success

def test_read_stamp():
    check_read_stamp(False,False,True)
    check_read_stamp(False,True,False)
    check_read_stamp(True,True,True)
