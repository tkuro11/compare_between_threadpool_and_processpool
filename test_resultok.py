from _pytest.capture import _windowsconsoleio_workaround
import pytest

from comparison import sumup, sumup_numpy, sequential, threadpool, processpool


def make_division(n: int, nthread: int) -> list[range]:
    div = n // nthread
    return [range(div * i + 1, div * i + div + 1) for i in range(nthread)]


N = 1_000_000
SUM_EXPECTED = (1 + N) * N // 2


@pytest.mark.parametrize("nthread", [10, 20])
@pytest.mark.parametrize(
    "runner, max_wks, worker",
    [
        (sequential, 1, sumup),
        (threadpool, 10, sumup),
        (sequential, 1, sumup_numpy),
        (threadpool, 10, sumup_numpy),
    ],
)
def test_result_fast(nthread, runner, max_wks, worker):
    division = make_division(N, nthread)
    assert runner(division, max_wks, sumup) == SUM_EXPECTED


@pytest.mark.slow
@pytest.mark.unstable
@pytest.mark.parametrize("nthread", [10, 20])
@pytest.mark.parametrize(
    "runner, max_wks, worker",
    [
        (processpool, 10, sumup),
        (processpool, 10, sumup_numpy),
    ],
)
def test_result_unstable(nthread, runner, max_wks, worker):
    division = make_division(N, nthread)
    assert runner(division, max_wks, worker) == SUM_EXPECTED
