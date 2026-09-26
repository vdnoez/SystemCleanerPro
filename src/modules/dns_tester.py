"""DNS-Leak-Tester — prüft DNS-Konfiguration und öffentliche IP."""
import socket
import subprocess
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# Bekannte DNS-Server (Präfix → Name)
KNOWN_DNS = {
    "1.1.1.1": "Cloudflare",
    "1.0.0.1": "Cloudflare",
    "8.8.8.8": "Google",
    "8.8.4.4": "Google",
    "9.9.9.9": "Quad9",
    "149.112.112.112": "Quad9",
    "208.67.222.222": "OpenDNS",
    "208.67.220.220": "OpenDNS",
    "76.76.2.0": "ControlD",
    "94.140.14.14": "AdGuard",
    "185.228.168.9": "CleanBrowsing",
}


def get_dns_servers_powershell() -> dict:
    """Liest DNS-Server aller Adapter via PowerShell."""
    ps_cmd = (
        'Get-DnsClientServerAddress -AddressFamily IPv4 | '
        'Where-Object {$_.ServerAddresses.Count -gt 0} | '
        'Select-Object InterfaceAlias, ServerAddresses | '
        'ConvertTo-Json -Compress'
    )
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            return {}
        out = result.stdout.strip()
        if not out or out == "null":
            return {}
        data = json.loads(out)
        if isinstance(data, dict):
            data = [data]

        adapters = {}
        for a in data:
            name = a.get("InterfaceAlias", "?")
            servers = a.get("ServerAddresses", [])
            if isinstance(servers, str):
                servers = [servers]
            adapters[name] = servers
        return adapters
    except Exception:
        return {}


def identify_dns(ip: str) -> str:
    """Erkennt DNS-Provider anhand der IP."""
    if ip in KNOWN_DNS:
        return KNOWN_DNS[ip]
    # Router-typische Adressen
    if ip.startswith("192.168.") or ip.startswith("10."):
        return "Router (lokal)"
    if ip.startswith("172.16.") or ip.startswith("172.17.") or ip.startswith("172.18."):
        return "Router (lokal)"
    if ip.startswith("127."):
        return "Localhost"
    return "Unbekannt"


def get_public_ip() -> dict:
    """Holt öffentliche IP + Provider."""
    if not HAS_REQUESTS:
        return {"error": "requests fehlt"}
    try:
        r = requests.get("https://ipapi.co/json/", timeout=8)
        if r.status_code != 200:
            return {"error": f"HTTP {r.status_code}"}
        data = r.json()
        return {
            "ip": data.get("ip", "?"),
            "city": data.get("city", ""),
            "country": data.get("country_name", ""),
            "isp": data.get("org", ""),
            "asn": data.get("asn", ""),
        }
    except Exception as e:
        return {"error": str(e)}


def get_cloudflare_trace() -> dict:
    """Holt Cloudflare-Trace (zeigt ob DNS zu Cloudflare geht)."""
    if not HAS_REQUESTS:
        return {}
    try:
        r = requests.get("https://1.1.1.1/cdn-cgi/trace", timeout=8)
        if r.status_code != 200:
            return {}
        data = {}
        for line in r.text.strip().split("\n"):
            if "=" in line:
                k, v = line.split("=", 1)
                data[k] = v
        return data
    except Exception:
        return {}


def test_dns_resolution() -> dict:
    """Testet DNS-Auflösung für bekannte Domains."""
    tests = [
        ("google.com", "8.8.8.8"),        # Sollte Google-IP zurückgeben
        ("cloudflare.com", "1.1.1.1"),    # Sollte Cloudflare-IP zurückgeben
        ("github.com", None),
    ]
    results = []
    for domain, expected_dns in tests:
        try:
            import time
            start = time.time()
            ip = socket.gethostbyname(domain)
            duration = (time.time() - start) * 1000
            results.append({
                "domain": domain,
                "resolved_ip": ip,
                "duration_ms": int(duration),
                "ok": True,
            })
        except Exception as e:
            results.append({
                "domain": domain,
                "resolved_ip": None,
                "duration_ms": 0,
                "ok": False,
                "error": str(e),
            })
    return {"tests": results}


def run_full_test(progress_cb=None) -> dict:
    """Führt alle Tests aus."""
    result = {
        "dns_servers": {},
        "public_ip": {},
        "cloudflare": {},
        "resolution": {},
    }

    if progress_cb:
        progress_cb("Lese DNS-Server...")
    result["dns_servers"] = get_dns_servers_powershell()

    if progress_cb:
        progress_cb("Hole öffentliche IP...")
    result["public_ip"] = get_public_ip()

    if progress_cb:
        progress_cb("Cloudflare-Trace...")
    result["cloudflare"] = get_cloudflare_trace()

    if progress_cb:
        progress_cb("Teste DNS-Auflösung...")
    result["resolution"] = test_dns_resolution()

    return result