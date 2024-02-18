from io import StringIO,BytesIO
from typing import BinaryIO


def copy(src:StringIO|BytesIO|BinaryIO, dst:StringIO|BytesIO|BinaryIO, buffSize=4 * 1024)->int:
    """
    copy src stream to dst stream with buffer
    """
    total = 0
    while True:
        buff = src.read(buffSize)
        if not buff:
            break
        dst.write(buff)
        total += len(buff)
    return total
