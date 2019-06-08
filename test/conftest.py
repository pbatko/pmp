import pytest
from pmp.preferences import Ordinal


@pytest.fixture
def ordinal():
    order = [5, 4, 3, 2, 1]
    weights = [1, 2, 3, 4, 5]
    return Ordinal(order, weights)


@pytest.fixture
def ordinal_factory():
    def _ordinal(size):
        order = [i + 1 for i in range(size)]
        weights = [i + 1 for i in range(size)]
        return Ordinal(order, weights)

    return _ordinal