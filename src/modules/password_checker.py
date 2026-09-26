"""Passwort-Checker via HaveIBeenPwned (k-Anonymität)."""
import hashlib
import secrets
import string

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


HIBP_API = "https://api.pwnedpasswords.com/range/"


def check_password(password: str) -> dict:
    """
    Prüft ein Passwort gegen HaveIBeenPwned.
    Nutzt k-Anonymität: nur die ersten 5 Zeichen des SHA-1-Hashes
    werden gesendet.
    """
    if not password:
        return {"error": "Passwort ist leer"}

    if not HAS_REQUESTS:
        return {"error": "requests-Bibliothek fehlt"}

    # SHA-1 Hash lokal berechnen
    sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]

    try:
        r = requests.get(HIBP_API + prefix, timeout=10)
        if r.status_code != 200:
            return {"error": f"API-Fehler: HTTP {r.status_code}"}

        # Antwort parsen: "HASH_SUFFIX:COUNT" pro Zeile
        for line in r.text.splitlines():
            if ":" not in line:
                continue
            h, count = line.split(":", 1)
            if h == suffix:
                return {
                    "pwned": True,
                    "count": int(count),
                    "message": f"⚠️  Dieses Passwort taucht in "
                               f"{int(count):,} Datenlecks auf!",
                }

        return {
            "pwned": False,
            "count": 0,
            "message": "✅ Dieses Passwort ist in keinen bekannten "
                       "Datenlecks aufgetaucht.",
        }

    except requests.Timeout:
        return {"error": "Zeitüberschreitung — Internet prüfen"}
    except Exception as e:
        return {"error": str(e)}


def generate_password(length: int = 20,
                      use_symbols: bool = True) -> str:
    """Generiert ein starkes Zufallspasswort."""
    chars = string.ascii_letters + string.digits
    if use_symbols:
        chars += "!@#$%^&*()-_=+[]{};:,.<>?/"

    # Mindestens 1 aus jeder Kategorie
    pw = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
    ]
    if use_symbols:
        pw.append(secrets.choice("!@#$%^&*()-_=+"))

    # Rest auffüllen
    while len(pw) < length:
        pw.append(secrets.choice(chars))

    # Mischen
    secrets.SystemRandom().shuffle(pw)
    return "".join(pw)


def password_strength(password: str) -> dict:
    """Bewertet Passwort-Stärke lokal (0-100)."""
    score = 0
    feedback = []

    if len(password) >= 8:
        score += 20
    else:
        feedback.append("Zu kurz (min. 8 Zeichen)")

    if len(password) >= 12:
        score += 15
    if len(password) >= 16:
        score += 15

    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in "!@#$%^&*()-_=+[]{};:,.<>?/" for c in password)

    if has_lower: score += 10
    else: feedback.append("Keine Kleinbuchstaben")
    if has_upper: score += 10
    else: feedback.append("Keine Großbuchstaben")
    if has_digit: score += 10
    else: feedback.append("Keine Zahlen")
    if has_symbol: score += 10
    else: feedback.append("Keine Sonderzeichen")

    score = min(100, score)

    if score >= 80:
        label, color = "Sehr stark", "#10b981"
    elif score >= 60:
        label, color = "Stark", "#22c55e"
    elif score >= 40:
        label, color = "Mittel", "#f59e0b"
    elif score >= 20:
        label, color = "Schwach", "#ef4444"
    else:
        label, color = "Sehr schwach", "#dc2626"

    return {
        "score": score,
        "label": label,
        "color": color,
        "feedback": feedback,
        "length": len(password),
    }