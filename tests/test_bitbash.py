from ncd.read import lesqlite2_read

def lesqlite2_write(value: int) -> bytearray:
    if value < 178:
        return bytearray([value])
    elif value < 16562:
        return bytearray([
             ((value-178) >> 8) + 178,
             ((value-178) & 0xFF)
        ])
    elif value < 540850:
        return bytearray([
            ((value-16562) >> 16) + 242,
            (((value-16562) & 0xFF00) >> 8),
            (((value-16562) & 0xFF))
        ])
    else:
        out = [247]
        while value > 0:
            out.append(value&0xFF)
            value >>= 8
            out[0] += 1
        return bytearray(out)

def check_lesqlite2_value(v):
    bytes = lesqlite2_write(v)
    (got_value,got_len) = lesqlite2_read(bytes)
    assert got_value == v
    assert got_len == len(bytes)

def test_lessqlite2():
    for i in range(0,1000000):
        check_lesqlite2_value(i)
    for bits in range(6,60):
        for wiggle in range(0,9):
            check_lesqlite2_value((1<<bits)+wiggle-4)
