#!/usr/bin/env python

import time
from concurrent.futures import ProcessPoolExecutor

from copy_guardian import BoundedSemaphore


def run_in_remoteprocess(i):
    with BoundedSemaphore(3):
        enter_ts = time.time()
        time.sleep(1.0)
    return enter_ts


def test_bounded_semaphore():
    with ProcessPoolExecutor(5) as p:
        times = sorted(p.map(run_in_remoteprocess, (1, 2, 3, 4, 5)))

    assert times[1] - times[0] < 0.5
    assert times[2] - times[1] < 0.5

    assert times[3] - times[0] > 0.9

    assert times[2] - times[3] < 0.5
    assert times[3] - times[4] < 0.5
