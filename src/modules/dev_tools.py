"""Developer-Cleanup — nutzt jetzt externe Config."""
import os
from pathlib import Path
from typing import Iterator

from src.core.config_loader import get_dev_patterns, get_max_depth


def find_dev_temp(root: Path) -> Iterator[tuple[Path, int]]:
    """Findet Dev-Temp-Ordner anhand der Config-Patterns."""
    patterns = get_dev_patterns()
    max_depth = get_max_depth()
    root = root.resolve()

    for dirpath, dirnames, _ in os.walk(root):
        current = Path(dirpath)
        try:
            depth = len(current.relative_to(root).parts)
        except ValueError:
            continue

        if depth > max_depth:
            dirnames.clear()
            continue

        for d in list(dirnames):
            if d in patterns:
                full = current / d
                yield full, dir_size(full)
                dirnames.remove(d)  # nicht tiefer gehen


def dir_size(path: Path) -> int:
    total = 0
    try:
        for f in path.rglob("*"):
            try:
                if f.is_file():
                    total += f.stat().st_size
            except OSError:
                continue
    except OSError:
        pass
    return total


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def delete_path(path: Path, to_trash: bool = True) -> tuple[bool, str]:
    """
    Löscht eine Datei/einen Ordner.
    to_trash=True  → Papierkorb (rückholbar)
    to_trash=False → endgültig
    Returns: (erfolg, fehlermeldung)
    """
    try:
        if to_trash:
            from send2trash import send2trash
            send2trash(str(path))
        else:
            import shutil
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=False)
            else:
                path.unlink()
        return True, ""
    except Exception as e:
        return False, str(e)