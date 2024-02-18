"""Utility functions for micpy."""

import sys
import time


def progress_indicator(iterable, description="Progress", unit="Iteration", start=1):
    """Progress indicator for iterable."""

    start_time = time.time()
    for i, item in enumerate(iterable, start=start):
        yield item
        elapsed_time = time.time() - start_time
        average_time = elapsed_time / i

        print(
            f"\r{description}: {unit} {i}. Elapsed Time: {elapsed_time:.2f}s. Average Time/{unit}: {average_time:.2f}s",
            end="",
        )
        # The print method's flush is not guaranteed to work in IPython environments. A
        # workaround is to use sys.stdout.flush() instead.
        sys.stdout.flush()


def is_compressed(filename):
    """Check if a file is compressed."""

    with open(filename, "rb") as f:
        return f.read(2) == b"\x1f\x8b"  # gzip magic number
