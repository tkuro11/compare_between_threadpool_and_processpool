import pytest

from comparison import sumup, sumup_numpy, sequential, threadpool, processpool


@pytest.fixture
def div(request):
    n, nthread = request.param
    div = n // nthread
    division = [range(div * i + 1, div * i + div + 1) for i in range(nthread)]
    return division


N = 1_000_000
SUM_EXPECTED = (1 + N) * N // 2


@pytest.mark.parametrize("div", [(N, 10), (N, 20)], indirect=True)
def test_sequential_result(div):
    assert sequential(div, 1, sumup) == SUM_EXPECTED


@pytest.mark.parametrize("div", [(N, 10), (N, 20)], indirect=True)
def test_threadpool_result(div):
    assert threadpool(div, 10, sumup) == SUM_EXPECTED


@pytest.mark.parametrize("div", [(N, 10), (N, 20)], indirect=True)
def test_processpool_result(div):
    assert processpool(div, 10, sumup) == SUM_EXPECTED


@pytest.mark.parametrize("div", [(N, 10), (N, 20)], indirect=True)
def test_sequential_numpy_result(div):
    assert sequential(div, 1, sumup_numpy) == SUM_EXPECTED


@pytest.mark.parametrize("div", [(N, 10), (N, 20)], indirect=True)
def test_threadpool_numpy_result(div):
    assert threadpool(div, 10, sumup_numpy) == SUM_EXPECTED


@pytest.mark.parametrize("div", [(N, 10), (N, 20)], indirect=True)
def test_processpool_numpy_result(div):
    assert processpool(div, 10, sumup_numpy) == SUM_EXPECTED
