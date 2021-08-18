import requests

class NCDAccessor:
    def read(self,offset: int,length: int):
        raise NotImplementedError("read() unimplemented in NCDReader")

class NCDFileAccessor(NCDAccessor):
    def __init__(self,filename: str):
        self.file = open(filename,"r+b")

    def read(self, offset: int, length: int) -> bytearray:
        out = bytearray()
        self.file.seek(offset)
        while length > 0:
            more = self.file.read(length)
            if len(more) == 0:
                raise IOError("Unexpected EOF")
            length -= len(more)
            out += more
        return out

class NCDBytesReader(NCDAccessor):
    def __init__(self,bytes: bytearray):
        self.bytes = bytes

    def read(self, offset: int, length: int) -> bytearray:
        return self.bytes[offset:offset+length]

# XXX timeouts
class NCDHttpAccessor(NCDAccessor):
    def __init__(self, url: str):
        self._url = url

    def read(self, offset: int, length: int) -> bytearray:
        if length == 0:
            return b""
        headers = {
            'range': "bytes={0}-{1}".format(offset,offset+length-1)
        }
        r = requests.get(self._url, headers=headers)
        if r.status_code > 299:
            raise IOError("bad http request")
        return r.content
