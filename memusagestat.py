import sys
import matplotlib.pyplot as plt
import matplotlib as mpl
import struct

from dataclasses import dataclass
from typing import List, Tuple, TypeVar

FORMAT = "QQII"  # u64, u64, u32, u32
SIZE = struct.calcsize(FORMAT)
assert SIZE == 8 + 8 + 4 + 4

@dataclass
class ParsedEntry:
    heap: int # U64
    stack: int # U64
    time_low: int  # U32
    time_high: int # U32

@dataclass
class Entry:
    heap: int  # U64
    stack: int  # U64
    time: int  # U64

def parse(slice: bytes) -> ParsedEntry:
    parts = struct.unpack(FORMAT, slice)
    heap, stack, low, high = parts
    return ParsedEntry(heap, stack, low, high)

def time(entry: ParsedEntry, start=0, scale=1) -> Entry:
    """Compute the time in [UNIT]

    Start is an offset *before* the scale is applied.
    Parse the first entry to find the start time.
    """
    time = entry.time_high << 32 | entry.time_low
    time -= start
    time /= scale
    return Entry(entry.heap, entry.stack, time)

T = List[int]
def plot(stacks: T, heaps: T, times: T, *, image: str):
    fix, ax = plt.subplots()
    # ax.plot(range(len(times)), heaps)
    ax.plot(times, heaps, linestyle=None, label="heap")
    plt.savefig(image)
    print(f"Saved {image}")


def main(datafile: str, imagefile: str):
    data = open(sys.argv[1], 'rb').read()
    count = int(len(data) / SIZE) - 2

    stacks = [0] * count
    heaps = [0] * count
    times = [0] * count
    entries = [None] * count  # type: List[Entry]

    headers = [
        parse(data[0:SIZE]),
        parse(data[SIZE:2*SIZE]),
    ]

    first = time(parse(data[2*SIZE: 3*SIZE]))

    for i in range(count):
        start = 2*SIZE + SIZE*i
        end = 2*SIZE + SIZE*i + SIZE
        entry = time(parse(data[start:end]), start=first.time, scale=1e10)
        entries[i] = entry

    # The data files contains buffered entries,
    # so the time is usually increasing but a different chunk can jump backward.
    entries = sorted(entries, key = lambda e: e.time)

    for i, entry in enumerate(entries):
        if i > 0:
            before = entries[i - 1].time
            now = entry.time
            if before > now:
                print(f"Warning: backwards time: {i-1}: {before}, {i}: {now}")

        stacks[i] = entry.stack
        heaps[i] = entry.heap
        times[i] = entry.time


    plot(stacks, heaps, times, image = imagefile)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
