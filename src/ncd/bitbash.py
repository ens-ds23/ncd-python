from typing import Tuple
from .util import NCDException

def lesqlite2_read(bytes: bytearray) -> Tuple[int,int]:
    if len(bytes) < 1:
        raise NCDException("bad lesqlite integer")
    b0 = bytes[0]
    if b0 < 178:
        return (b0,1)
    if len(bytes) < 2:
        raise NCDException("bad lesqlite integer")
    b1 = bytes[1]
    if b0 < 242:
        return (178 + ((b0-178)<<8) + b1, 2)
    if len(bytes) < 3:
        raise NCDException("bad lesqlite integer")
    b2 = bytes[2]
    if b0 < 250:
        return (16562+(((b0-242)<<16)+(b1<<8)+b2),3)
    n = b0-247
    if len(bytes) <= n:
        raise NCDException("bad lesqlite integer")
    v = 0
    shift = 0
    for i in range(0,n):
        v += bytes[i+1] << shift
        shift += 8
    return (v,n+1)
