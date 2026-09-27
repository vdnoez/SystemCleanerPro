"""Download-Statistik via GitHub API."""
import requests
from datetime import datetime, timedelta, timezone

from src.core.config import GITHUB_API, GITHUB_USER, GITHUB_REPO


def get_all_releases() -> list:
    """Holt alle Releases + Assets von GitHub."""
    try:
        r = requests.get(
            f"{GITHUB_API}/releases?per_page=100",
            timeout=15,
            headers={"Accept": "application/vnd.github+json"}
        )
        if r.status_code != 200:
            return []
        return r.json()
    except Exception:
        return []


def get_total_downloads() -> int:
    """Zählt alle Downloads über alle Releases."""
    releases = get_all_releases()
    total = 0
    for rel in releases:
        for asset in rel.get("assets", []):
            total += asset.get("download_count", 0)
    return total


def get_release_stats() -> list:
    """Gibt pro Release die Download-Zahlen."""
    releases = get_all_releases()
    stats = []

    for rel in releases:
        tag = rel.get("tag_name", "?")
        published = rel.get("published_at", "")
        prerelease = rel.get("prerelease", False)

        total = 0
        assets = []
        for asset in rel.get("assets", []):
            count = asset.get("download_count", 0)
            total += count
            assets.append({
                "name": asset.get("name", "?"),
                "size_mb": round(asset.get("size", 0) / (1024 * 1024), 1),
                "downloads": count,
            })

        # Datum parsen
        try:
            dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
            date_str = dt.strftime("%d.%m.%Y")
            days_ago = (datetime.now(timezone.utc) - dt).days
        except Exception:
            date_str = "?"
            days_ago = 0

        stats.append({
            "tag": tag,
            "name": rel.get("name", tag),
            "published": date_str,
            "days_ago": days_ago,
            "published_iso": published,
            "prerelease": prerelease,
            "total_downloads": total,
            "assets": assets,
            "url": rel.get("html_url", ""),
        })

    # Nach Datum sortieren (neueste zuerst)
    stats.sort(key=lambda x: x.get("published_iso", ""), reverse=True)
    return stats


def get_summary() -> dict:
    """Zusammenfassung für Anzeige."""
    releases = get_release_stats()

    total = sum(r["total_downloads"] for r in releases)
    latest = releases[0] if releases else None

    # Heute / Woche
    today = 0
    week = 0
    for r in releases:
        if r["days_ago"] == 0:
            today += r["total_downloads"]
        if r["days_ago"] <= 7:
            week += r["total_downloads"]

    # Bester Tag (vereinfacht — pro Release)
    best = max(releases, key=lambda r: r["total_downloads"]) if releases else None

    return {
        "total": total,
        "release_count": len(releases),
        "today": today,
        "week": week,
        "latest_version": latest["tag"] if latest else "—",
        "latest_downloads": latest["total_downloads"] if latest else 0,
        "best_release": best["tag"] if best else "—",
        "best_release_downloads": best["total_downloads"] if best else 0,
    }


def get_downloads_over_time() -> list:
    """
    Liefert pro Tag die geschätzten Downloads.
    (GitHub gibt nur kumulativ pro Release — wir verteilen
    die Downloads gleichmäßig über die Tage seit Release.)
    """
    releases = get_release_stats()
    daily = {}

    for rel in releases:
        count = rel["total_downloads"]
        days = max(1, rel["days_ago"])
        per_day = count / days if days > 0 else count

        for i in range(days):
            day = (datetime.now(timezone.utc) -
                   timedelta(days=i)).strftime("%d.%m.")
            daily[day] = daily.get(day, 0) + per_day

    # Sortieren nach Datum (umgekehrt)
    sorted_days = []
    for i in range(30):  # letzte 30 Tage
        day = (datetime.now(timezone.utc) -
               timedelta(days=i)).strftime("%d.%m.")
        sorted_days.append({
            "day": day,
            "downloads": int(daily.get(day, 0)),
        })

    return list(reversed(sorted_days))