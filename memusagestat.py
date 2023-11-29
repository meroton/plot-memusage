#!/usr/bin/env python3

import argparse
import matplotlib.pyplot as plt
import struct
import sys

from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Tuple, TypeVar

FORMAT = "QQII"  # u64, u64, u32, u32
SIZE = struct.calcsize(FORMAT)
assert SIZE == 8 + 8 + 4 + 4


@dataclass
class ParsedEntry:
    heap: int  # u64
    stack: int  # u64
    time_low: int  # u32
    time_high: int  # u32


@dataclass
class Entry:
    heap: int  # u64
    stack: int  # u64
    time: int  # u64


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


def plot(
    *,
    stacks: List[int],
    heaps: List[int],
    xaxis: Tuple[List[int], str],
    image: str,
    total: bool,
    title: Optional[str] = None,
):
    xs, xlabel = xaxis

    fix, ax = plt.subplots()
    ax.plot(xs, heaps, '.-', markersize=1, label="Heap", color="red")
    ax.plot(xs, stacks, '.-', markersize=1, label="Stack", color="green")

    if total:
        totals = [0] * len(xs)
        for i in range(len(xs)):
            totals[i] = stacks[i] + heaps[i]
        ax.plot(xs, totals, linestyle=None, label="Total", color="black")

    if title:
        ax.set_title(title)

    ax.set_xlabel(xlabel)
    ax.set_ylabel("Size [byte]")

    plt.legend()

    fig.tight_layout()
    plt.savefig(image)
    print(f"Saved {image}")


def arguments(args: List[str]):
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", help="Graph title")
    parser.add_argument(
        "-T",
        "--total",
        help="Also draw graph for total memory consumption",
        action="store_true",
    )
    parser.add_argument(
        "-t",
        "--time",
        help="Generate output linear to time (default is linear to number of function calls)",
        action="store_true",
    )
    parser.add_argument("datafile", help="Datafile from `memusage`")
    parser.add_argument("imagefile", help="Output filename for the plot")

    return parser.parse_args(args)


def main(
    datafile: str,
    imagefile: str,
    *,
    title: str,
    plot_time: bool,
    total: bool,
):
    xtransformer, xlabel = {
        True: (lambda x: x, "Time [s]"),
        False: (lambda x: range(len(x)), "Linear allocations [#]"),
    }[plot_time]

    data = open(sys.argv[1], "rb").read()
    count = int(len(data) / SIZE) - 2

    stacks = [0] * count
    heaps = [0] * count
    times = [0] * count
    entries: List[Entry] = [Entry(0, 0, 0)] * count

    headers = [
        parse(data[0:SIZE]),
        parse(data[SIZE : 2 * SIZE]),
    ]

    first = time(parse(data[2 * SIZE : 3 * SIZE]))

    for i in range(count):
        start = 2 * SIZE + SIZE * i
        end = 2 * SIZE + SIZE * i + SIZE
        entry = time(parse(data[start:end]), start=first.time, scale=1e10)
        entries[i] = entry

    # The data files contains buffered entries,
    # so the time is usually increasing but a different chunk can jump backward.
    entries = sorted(entries, key=lambda e: e.time)

    for i, entry in enumerate(entries):
        if i > 0:
            before = entries[i - 1].time
            now = entry.time
            if before > now:
                print(f"Warning: backwards time: {i-1}: {before}, {i}: {now}")

        stacks[i] = entry.stack
        heaps[i] = entry.heap
        times[i] = entry.time

    plot(
        title=title,
        stacks=stacks,
        heaps=heaps,
        xaxis=(xtransformer(times), xlabel),
        image=imagefile,
        total=total,
    )


if __name__ == "__main__":
    args = arguments(sys.argv[1:])

    main(
        args.datafile,
        args.imagefile,
        title=args.title,
        plot_time=args.time,
        total=args.total,
    )
