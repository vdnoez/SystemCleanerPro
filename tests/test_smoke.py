from src.modules.performance import get_snapshot
from src.modules.dev_tools import human_size


def test_snapshot():
    s = get_snapshot()
    assert 0 <= s.cpu <= 100
    assert 0 <= s.ram <= 100


def test_human_size():
    assert human_size(1024) == "1.0 KB"
    assert human_size(0) == "0.0 B"
