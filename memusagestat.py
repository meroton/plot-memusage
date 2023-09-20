import sys
import struct
from dataclasses import dataclass
from typing import List

FORMAT = "qqii"  # i64, i64, i32, i32
SIZE = struct.calcsize(FORMAT)
assert SIZE == 8 + 8 + 4 + 4

@dataclass
class ParsedEntry:
    heap: int
    stack: int
    time_high: int
    time_low: int

@dataclass
class Entry:
    heap: int
    stack: int
    time: int

def parse(slice: bytes) -> ParsedEntry:
    parts = struct.unpack(FORMAT, slice)
    heap, stack, high, low = parts
    return ParsedEntry(heap, stack, high, low)

def time(entry: ParsedEntry) -> Entry:
    """Compute the time in [UNIT]"""
    time = entry.time_high << 32 | entry.time_low
    return Entry(entry.heap, entry.stack, time)

def main(datafile: str):
    data = open(sys.argv[1], 'rb').read()

    headers = [time(parse(data[x:x+SIZE]))
              for x in [0, SIZE]]

    print(headers)

if __name__ == '__main__':
    main(sys.argv[1])
