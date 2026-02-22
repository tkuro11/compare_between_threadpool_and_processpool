from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass
from timeit import default_timer
import numpy as np
from typing import Callable


def sumup(r: range) -> int:
    count = 0
    for i in r:
        count += i
    return count


def sumup_numpy(r: range) -> int:
    return np.sum(np.arange(r.start, r.stop, dtype=int))


def sequential(division: list[range], maxworker: int, worker: Callable) -> int:
    count = 0
    for area in division:
        count += worker(area)
    return count


def threadpool(division: list[range], maxworker: int, worker: Callable) -> int:
    count = 0
    with ThreadPoolExecutor(max_workers=maxworker) as executor:
        for subcount in executor.map(worker, division):
            count += subcount
        return count


def processpool(division: list[range], maxworker: int, worker: Callable) -> int:
    count = 0
    with ProcessPoolExecutor(max_workers=maxworker) as executor:
        for subcount in executor.map(worker, division):
            count += subcount
    return count


def timeit(
    func: Callable, values: list[range], maxworker: int = 1, worker: Callable = sumup
) -> None:
    worker_message = f"(max_wks = {maxworker})" if func != sequential else ""

    bt = default_timer()
    func(values, maxworker, worker)
    print(
        f"{func.__name__}.{worker.__name__}{worker_message} elapsed time : {default_timer() - bt}"
    )


def main():
    #### comparison setup
    nthread = 10
    n = 100_000_000
    div = n // nthread
    division = [range(div * i + 1, div * i + div + 1) for i in range(nthread)]

    print("#### SEQUENTIAL ####")
    timeit(sequential, division)

    print("#### ThreadPool ####")
    for maxworker in range(1, 13):
        timeit(threadpool, division, maxworker)

    print("#### ProcessPool ####")
    for maxworker in range(1, 13):
        timeit(processpool, division, maxworker)

    # numpy calculation is too fast, so need to increase the data
    n = 1_000_000_000
    div = n // nthread
    division = [RANGE(div * i + 1, div * i + div + 1) for i in range(nthread)]

    print("#### SEQUENTIAL-Numpy ####")
    timeit(sequential, division, 1, sumup_numpy)

    print("#### ThreadPool-Numpy ####")
    for maxworker in range(1, 13):
        timeit(threadpool, division, maxworker, sumup_numpy)

    print("#### ProcessPool-Numpy ####")
    for maxworker in range(1, 13):
        timeit(processpool, division, maxworker, sumup_numpy)


if __name__ == "__main__":
    main()
