import sys
import matplotlib.pyplot as plt
import matplotlib as mpl
import struct

from dataclasses import dataclass
from typing import List, Tuple, TypeVar

FORMAT = "QQII"  # i64, i64, i32, i32
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

def parse(slice: bytes) -> Tuple[int, int, int]:
    parts = struct.unpack(FORMAT, slice)
    heap, stack, time_high, time_low = parts
    # time = time_high << 32 | time_low
    time = time_high
    return heap, stack, time

T = List[int]
def plot(stacks: T, heaps: T, times: T):
    # NB: `matplotlib` does not like 64 bit times.
    fix, ax = plt.subplots()
    # ax.plot(range(len(times)), stacks)
    ax.plot(times, stacks)
    plt.savefig('foo.png')
    print("Saved!")


def main(datafile: str):
    data = open(sys.argv[1], 'rb').read()
    count = int(len(data) / SIZE) - 2

    stacks = [0] * count
    heaps = [0] * count
    times = [0] * count

    headers = [
        parse(data[0:SIZE]),
        parse(data[SIZE:2*SIZE]),
    ]

    for i in range(count):
        start = 2*SIZE + SIZE*i
        end = 2*SIZE + SIZE*i + SIZE
        h, s, t = parse(data[start:end])
        stacks[i] = s
        heaps[i] = h
        times[i] = t

        if i > 0:
            before = times[i - 1]
            if before > t:
                print(f"Warning: backwards time: {i-1}: {before}, {i}: {t}")

    print(headers)
    print(times[:10])
    plot(stacks, heaps, times)


if __name__ == '__main__':
    main(sys.argv[1])
