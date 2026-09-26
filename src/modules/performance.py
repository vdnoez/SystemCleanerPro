"""Performance."""
import psutil
from dataclasses import dataclass


@dataclass
class Snapshot:
    cpu: float
    ram: float
    disk: float


def get_snapshot() -> Snapshot:
    return Snapshot(
        cpu=psutil.cpu_percent(interval=0.2),
        ram=psutil.virtual_memory().percent,
        disk=psutil.disk_usage("C:/").percent,
    )


def top_cpu_hogs(n: int = 5):
    procs = []
    for p in psutil.process_iter(["name", "cpu_percent"]):
        try:
            procs.append((p.info["name"], p.info["cpu_percent"] or 0.0))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return sorted(procs, key=lambda x: x[1], reverse=True)[:n]
