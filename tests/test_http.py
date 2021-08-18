from ncd.accessor import NCDHttpAccessor
from ncd.read import NCDRead

URL = "https://raw.githubusercontent.com/ens-ds23/ncd/main/testdata/smoke.ncd";

def test_http():
    read = NCDRead(NCDHttpAccessor(URL))
    assert b"World" == read.get(b"Hello")
    assert b"Mars" == read.get(b"Goodbye")
    assert b"f" == read.get(b"e")
    assert None == read.get(b"a")
