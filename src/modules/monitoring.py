"""Monitoring."""
from collections import deque
from statistics import mean, pstdev
from src.modules.performance import get_snapshot

HISTORY = deque(maxlen=100)


def sample():
    s = get_snapshot()
    e = {"cpu": s.cpu, "ram": s.ram, "disk": s.disk}
    HISTORY.append(e)
    return e


def is_anomaly(metric: str = "cpu", z_threshold: float = 3.0) -> bool:
    if len(HISTORY) < 20:
        return False
    values = [h[metric] for h in HISTORY]
    mu, sigma = mean(values), pstdev(values) or 1e-6
    return abs(values[-1] - mu) / sigma > z_threshold
