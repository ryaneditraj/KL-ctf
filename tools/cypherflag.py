#!/usr/bin/env python3
"""CypherFlag toolkit — recon + web helpers the agent should call via shell."""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

BRACE_FLAG_RE = re.compile(r"[A-Za-z0-9_\-]{2,32}\{[^}\n]{3,200}\}")
FLAG_LABEL_RE = re.compile(
    r"(?:FLAG|flag|CTF|ctf|UCSI|ucsi)\s*[:=]\s*(\S{4,160})"
)

# Operator-supplied .env may set only these. Anything else is ignored so a
# local env file cannot override PATH or other process settings.
_DOTENV_KEYS = {"CYPHERFLAG_TLS_VERIFY", "CYPHERFLAG_ALLOW_METADATA"}
_HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}
_METADATA_NAMES = {"metadata.google.internal", "metadata"}
_METADATA_IPS = {
    ipaddress.ip_address("169.254.169.254"),
    ipaddress.ip_address("169.254.170.2"),
    ipaddress.ip_address("fd00:ec2::254"),
}


def load_dotenv() -> None:
    """Load the allowlisted keys from the repo .env, without overriding the environment."""
    path = Path(__file__).resolve().parents[1] / ".env"
    if not path.is_file():
        return
    for raw in path.read_text(errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key not in _DOTENV_KEYS:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def _truthy(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def tls_verify_enabled() -> bool:
    """Verify TLS certificates unless the operator explicitly opts out."""
    return _truthy("CYPHERFLAG_TLS_VERIFY", default=True)


def metadata_allowed() -> bool:
    return _truthy("CYPHERFLAG_ALLOW_METADATA", default=False)


def _reject_controls(value: str, label: str) -> str:
    if "\x00" in value or "\n" in value or "\r" in value:
        raise ValueError(f"{label} contains an unsafe character")
    if value.startswith("-") or value.startswith("@"):
        raise ValueError(f"{label} must not start with '-' or '@'")
    return value


def _coerce_ip(host: str) -> ipaddress.IPv4Address | ipaddress.IPv6Address | None:
    text = host.strip().strip("[]").lower().rstrip(".")
    if text.startswith("0x"):
        try:
            number = int(text, 16)
        except ValueError:
            return None
        if 0 <= number <= 0xFFFFFFFF:
            return ipaddress.IPv4Address(number)
        return None
    if text.isdigit():
        number = int(text)
        if 0 <= number <= 0xFFFFFFFF:
            return ipaddress.IPv4Address(number)
    try:
        parsed = ipaddress.ip_address(text)
    except ValueError:
        return None
    if isinstance(parsed, ipaddress.IPv6Address) and parsed.ipv4_mapped is not None:
        return parsed.ipv4_mapped
    return parsed


def is_metadata_host(host: str) -> bool:
    name = host.strip().strip("[]").lower().rstrip(".")
    if name in _METADATA_NAMES or name.endswith(".metadata.google.internal"):
        return True
    parsed = _coerce_ip(name)
    return parsed in _METADATA_IPS if parsed is not None else False


def _reject_metadata(host: str) -> None:
    if is_metadata_host(host) and not metadata_allowed():
        raise ValueError(
            "cloud metadata hosts are blocked; set CYPHERFLAG_ALLOW_METADATA=1 "
            "only inside an authorized lab"
        )


def guard_host(target: str) -> str:
    if not isinstance(target, str):
        raise ValueError("target must be a string")
    target = target.strip()
    _reject_controls(target, "target")
    if any(ch.isspace() for ch in target):
        raise ValueError("target must not contain whitespace")
    if not re.fullmatch(r"[A-Za-z0-9._:\-\[\]]{1,253}", target):
        raise ValueError("target has unexpected characters")
    _reject_metadata(target.strip("[]"))
    return target


def guard_method(method: str | None) -> str:
    verb = (method or "GET").strip().upper()
    if verb not in _HTTP_METHODS:
        raise ValueError("HTTP method is not allowed")
    return verb


def guard_url(url: str) -> str:
    if not isinstance(url, str):
        raise ValueError("url must be a string")
    url = url.strip()
    _reject_controls(url, "url")
    if any(ch.isspace() for ch in url):
        raise ValueError("url must not contain whitespace")
    if len(url) > 4096:
        raise ValueError("url is too long")
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("only http and https URLs are allowed")
    host = parsed.hostname
    if not host:
        raise ValueError("url is missing a host")
    _reject_metadata(host)
    return url


def guard_line(value: str, label: str) -> str:
    if not isinstance(value, str) or value.strip() == "":
        raise ValueError(f"{label} is empty")
    if len(value) > 8192:
        raise ValueError(f"{label} is too long")
    return _reject_controls(value, label)


def guard_data(value: str) -> str:
    """POST bodies may contain spaces and quotes, but not curl/sqlmap flag or file tricks."""
    if not isinstance(value, str):
        raise ValueError("data must be a string")
    if "\x00" in value:
        raise ValueError("data contains an unsafe character")
    if value.startswith("-") or value.startswith("@"):
        raise ValueError("data must not start with '-' or '@'")
    if len(value) > 1_000_000:
        raise ValueError("data is too long")
    return value


def guard_wordlist(path: str) -> str:
    path = guard_line(path, "wordlist")
    candidate = Path(path)
    if not candidate.is_file():
        raise ValueError("wordlist must be an existing local file")
    return str(candidate)


def _silence_insecure_warning() -> None:
    try:
        import urllib3

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except Exception:  # noqa: BLE001
        pass


def guarded_session() -> Any:
    import requests

    session = requests.Session()
    session.headers["User-Agent"] = "CypherFlag/1.0"
    session.hooks["response"].append(_redirect_guard)
    return session


def _redirect_guard(response: Any, **kwargs: Any) -> Any:
    # A 3xx that the caller asked not to follow is evidence, not a hop.
    if kwargs.get("allow_redirects", True) is False:
        return response
    if not (response.is_redirect or response.is_permanent_redirect):
        return response
    location = response.headers.get("Location", "")
    if location:
        guard_url(urljoin(response.url, location))
    return response


def request_http(session: Any, method: str, url: str, **kwargs: Any) -> tuple[Any, bool]:
    """Return (response, used_insecure_tls).

    Certificates are verified by default. A single retry without verification
    keeps authorized labs that use a self-signed certificate working.
    """
    import requests

    verify = bool(kwargs.pop("verify", tls_verify_enabled()))
    try:
        return session.request(method, url, verify=verify, **kwargs), False
    except requests.exceptions.SSLError:
        if not verify:
            raise
        _silence_insecure_warning()
        response = session.request(method, url, verify=False, **kwargs)
        return response, True


def run(cmd: list[str], timeout: int = 120) -> dict[str, Any]:
    try:
        p = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, check=False
        )
        return {
            "cmd": cmd,
            "rc": p.returncode,
            "stdout": p.stdout,
            "stderr": p.stderr,
        }
    except FileNotFoundError:
        return {"cmd": cmd, "rc": 127, "stdout": "", "stderr": f"missing: {cmd[0]}"}
    except subprocess.TimeoutExpired:
        return {"cmd": cmd, "rc": 124, "stdout": "", "stderr": "timeout"}


def dig_lookup(target: str) -> dict[str, Any]:
    target = guard_host(target)
    out: dict[str, Any] = {"target": target, "records": {}}
    for rtype in ("A", "AAAA", "MX", "TXT", "NS", "CNAME"):
        r = run(["dig", "+short", target, rtype], timeout=30)
        lines = [ln.strip() for ln in r["stdout"].splitlines() if ln.strip()]
        out["records"][rtype] = lines
    any_r = run(["dig", target, "ANY", "+noall", "+answer"], timeout=30)
    out["any_answer"] = any_r["stdout"]
    return out


def nmap_scan(target: str, full: bool = False, quick: bool = False) -> dict[str, Any]:
    target = guard_host(target)
    # `--` keeps a target from being parsed as an nmap option.
    if full:
        cmd = ["nmap", "-Pn", "-sV", "-sC", "-T4", "-p-", "--", target]
        timeout = 600
    elif quick:
        cmd = ["nmap", "-Pn", "-T4", "--top-ports", "100", "--", target]
        timeout = 90
    else:
        cmd = ["nmap", "-Pn", "-sV", "-sC", "-T4", "--top-ports", "1000", "--", target]
        timeout = 300
    r = run(cmd, timeout=timeout)
    return {"target": target, "full": full, "quick": quick, **r}



def curl_fetch(url: str, method: str = "GET", data: str | None = None) -> dict[str, Any]:
    url = guard_url(url)
    method = guard_method(method)
    if data is not None:
        data = guard_data(data)

    def build(header_flags: list[str]) -> list[str]:
        cmd = [
            "curl",
            "-sS",
            "-L",
            "--proto",
            "=http,https",
            "--proto-redir",
            "=http,https",
            "--max-time",
            "30",
            "-X",
            method,
            *header_flags,
        ]
        if data is not None:
            # --data-raw does not treat a leading @ as a local filename.
            cmd += ["--data-raw", data]
        cmd += ["--", url]
        return cmd

    # First request mirrors the historical -D - call; the parsed result is the -i call.
    run(build(["-D", "-"]), timeout=60)
    r2 = run(build(["-i"]), timeout=60)
    text = r2["stdout"]
    flags = extract_flags(text)
    return {"url": url, "method": method, **r2, "flags_found": flags}


def extract_flags(text: str) -> list[str]:
    found: list[str] = []
    for m in BRACE_FLAG_RE.finditer(text or ""):
        g = m.group(0).strip()
        if g not in found:
            found.append(g)
    for m in FLAG_LABEL_RE.finditer(text or ""):
        g = m.group(1).strip().rstrip(".,;:)")
        if BRACE_FLAG_RE.fullmatch(g):
            if g not in found:
                found.append(g)
        elif g not in found and "{" not in g and len(g) >= 8:
            found.append(g)
    return found


def extract_targets(text: str) -> dict[str, list[str]]:
    urls = re.findall(r"https?://[^\s\)\]\"'<>]+", text or "")
    ips = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", text or "")
    hosts = re.findall(
        r"\b(?:[a-zA-Z0-9-]+\.)+(?:com|net|org|io|dev|local|ctf|xyz|me|edu|gov|co)\b",
        text or "",
        flags=re.I,
    )
    # dedupe preserve order
    def uniq(xs: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for x in xs:
            x = x.rstrip(".,);]")
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    return {"urls": uniq(urls), "ips": uniq(ips), "hosts": uniq(hosts)}


def load_paths() -> list[str]:
    wl = Path(__file__).resolve().parent / "wordlists" / "paths.txt"
    if not wl.exists():
        return ["/", "/flag", "/flag.txt", "/admin", "/login", "/robots.txt"]
    return [
        ln.strip()
        for ln in wl.read_text().splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]


def web_hunt(url: str) -> dict[str, Any]:
    """Aggressive CTF web pass: paths + simple injection smoke tests on forms."""
    url = guard_url(url)
    try:
        from bs4 import BeautifulSoup

        session = guarded_session()
    except ImportError:
        return {"error": "requests/bs4 missing", "fallback": curl_fetch(url)}

    out: dict[str, Any] = {"url": url, "hits": [], "flags_found": [], "form_probes": []}
    flags: list[str] = []

    def note_flags(src: str, label: str) -> None:
        for f in extract_flags(src):
            if f not in flags:
                flags.append(f)
                out["hits"].append({"where": label, "flag": f})

    def fetch(method: str, req_url: str, **kwargs: Any) -> Any:
        resp, fell_back = request_http(session, method, req_url, **kwargs)
        if fell_back:
            out["tls_verify_fallback"] = True
        return resp

    try:
        base_resp = fetch("GET", url, timeout=20, allow_redirects=True)
    except Exception as e:  # noqa: BLE001
        return {"url": url, "error": str(e)}

    note_flags(base_resp.text, "index")
    note_flags(str(base_resp.headers), "headers")
    parsed = urlparse(str(base_resp.url))
    base = f"{parsed.scheme}://{parsed.netloc}"

    for path in load_paths():
        try:
            r = fetch("GET", base + path, timeout=8, allow_redirects=True)
        except Exception:  # noqa: BLE001
            continue
        interesting = r.status_code in (200, 301, 302, 401, 403) or bool(
            extract_flags(r.text)
        )
        if interesting and r.status_code != 404:
            out["hits"].append(
                {
                    "path": path,
                    "status": r.status_code,
                    "len": len(r.content),
                    "flags": extract_flags(r.text),
                    "snippet": r.text[:200],
                }
            )
            note_flags(r.text, path)

    # form smoke: SSTI / SQLi / cmd lightly
    soup = BeautifulSoup(base_resp.text, "html.parser")
    probes = [
        ("ssti", "{{7*7}}"),
        ("ssti2", "${7*7}"),
        ("sqli", "' OR '1'='1' -- "),
        ("sqli2", "\" OR \"1\"=\"1\" -- "),
        ("union", "' UNION SELECT null,null,null-- "),
        ("cmd", "; id"),
        ("cmd2", "| id"),
        ("cmd3", "$(id)"),
        ("lfi", "../../../etc/passwd"),
        ("lfi2", "....//....//....//etc/passwd"),
        ("xss", "<script>alert(1)</script>"),
    ]
    for form in soup.find_all("form")[:5]:
        action = urljoin(str(base_resp.url), form.get("action") or "")
        try:
            guard_url(action)
        except ValueError as exc:
            out["form_probes"].append({"action": action, "error": str(exc)})
            continue
        method = (form.get("method") or "get").lower()
        inputs = [
            i
            for i in form.find_all(["input", "textarea"])
            if i.get("name") and (i.get("type") or "text") not in ("submit", "button", "image", "file")
        ]
        if not inputs:
            continue
        for kind, payload in probes:
            data = {i.get("name"): payload for i in inputs}
            try:
                if method == "post":
                    r = fetch("POST", action, data=data, timeout=10)
                else:
                    r = fetch("GET", action, params=data, timeout=10)
            except Exception as e:  # noqa: BLE001
                out["form_probes"].append({"action": action, "kind": kind, "error": str(e)})
                continue
            entry = {
                "action": action,
                "kind": kind,
                "status": r.status_code,
                "flags": extract_flags(r.text),
                "reflects_49": "49" in r.text,
                "snippet": r.text[:240],
            }
            out["form_probes"].append(entry)
            note_flags(r.text, f"form:{kind}")

    # Real scanners (ffuf / nuclei) — skip silently if not installed
    out["scanners"] = {}
    fuzz_url = base.rstrip("/") + "/FUZZ"
    try:
        out["scanners"]["ffuf"] = ffuf_scan(fuzz_url, quick=True)
    except ValueError as exc:
        out["scanners"]["ffuf"] = {"error": str(exc)}
    for f in out["scanners"]["ffuf"].get("flags_found") or []:
        if f not in flags:
            flags.append(f)
    try:
        out["scanners"]["nuclei"] = nuclei_scan(base, quick=True)
    except ValueError as exc:
        out["scanners"]["nuclei"] = {"error": str(exc)}
    for f in out["scanners"]["nuclei"].get("flags_found") or []:
        if f not in flags:
            flags.append(f)

    out["flags_found"] = flags
    return out


def have(cmd: str) -> bool:
    from shutil import which

    return which(cmd) is not None


def ffuf_scan(url_with_fuzz: str, wordlist: str | None = None, quick: bool = True) -> dict[str, Any]:
    """Directory/path fuzz with ffuf. URL must contain FUZZ."""
    url_with_fuzz = guard_url(url_with_fuzz)
    if "FUZZ" not in url_with_fuzz:
        raise ValueError("ffuf url must contain FUZZ")
    if wordlist is not None:
        wl = guard_wordlist(wordlist)
    else:
        wl = str(Path(__file__).resolve().parent / "wordlists" / "paths.txt")
    if not have("ffuf"):
        return {"error": "ffuf not installed", "fix": "bash scripts/install-mac-scanners.sh"}
    cmd = [
        "ffuf",
        "-u",
        url_with_fuzz,
        "-w",
        wl,
        "-mc",
        "200,204,301,302,307,401,403",
        "-t",
        "20",
        "-timeout",
        "5",
        "-of",
        "json",
        "-o",
        "/dev/stdout",
        "-s",
    ]
    if quick:
        cmd += ["-maxtime", "60"]
    r = run(cmd, timeout=90 if quick else 300)
    flags = extract_flags(r.get("stdout") or "") + extract_flags(r.get("stderr") or "")
    results = []
    try:
        data = json.loads(r["stdout"] or "{}")
        for row in data.get("results") or []:
            results.append(
                {
                    "status": row.get("status"),
                    "url": row.get("url"),
                    "length": row.get("length"),
                }
            )
            flags.extend(extract_flags(str(row)))
    except Exception:  # noqa: BLE001
        pass
    return {
        "cmd": cmd,
        "rc": r.get("rc"),
        "results": results[:50],
        "flags_found": list(dict.fromkeys(flags)),
        "stderr_tail": (r.get("stderr") or "")[-400:],
    }


def sqlmap_scan(url: str, data: str | None = None, quick: bool = True) -> dict[str, Any]:
    """sqlmap against a URL (authorized CTF only). batch + limited risk."""
    url = guard_url(url)
    if data is not None:
        data = guard_data(data)
    if not have("sqlmap"):
        return {"error": "sqlmap not installed", "fix": "bash scripts/install-mac-scanners.sh"}
    cmd = [
        "sqlmap",
        "-u",
        url,
        "--batch",
        "--random-agent",
        "--level=2" if quick else "--level=3",
        "--risk=1" if quick else "--risk=2",
        "--timeout=10",
        "--retries=1",
        "--technique=BEUSTQ",
    ]
    if data:
        cmd += ["--data", data]
    if quick:
        cmd += ["--time-sec=3", "--threads=2"]
    r = run(cmd, timeout=120 if quick else 420)
    blob = (r.get("stdout") or "") + "\n" + (r.get("stderr") or "")
    return {
        "cmd": cmd,
        "rc": r.get("rc"),
        "flags_found": extract_flags(blob),
        "interesting": [
            ln.strip()
            for ln in blob.splitlines()
            if any(
                k in ln.lower()
                for k in ("injectable", "fetched", "flag", "parameter", "payload", "database")
            )
        ][:40],
        "tail": blob[-800:],
    }


def nuclei_scan(url: str, quick: bool = True) -> dict[str, Any]:
    """nuclei exposures/misconfig (rate-limited)."""
    url = guard_url(url)
    if not have("nuclei"):
        return {"error": "nuclei not installed", "fix": "bash scripts/install-mac-scanners.sh"}
    cmd = [
        "nuclei",
        "-u",
        url,
        "-silent",
        "-jsonl",
        "-rate-limit",
        "50",
        "-timeout",
        "5",
        "-retries",
        "1",
    ]
    if quick:
        cmd += ["-tags", "exposure,misconfig,config,token,tech"]
        cmd += ["-severity", "info,low,medium,high,critical"]
    r = run(cmd, timeout=120 if quick else 400)
    findings = []
    flags: list[str] = []
    for ln in (r.get("stdout") or "").splitlines():
        flags.extend(extract_flags(ln))
        try:
            obj = json.loads(ln)
            findings.append(
                {
                    "template": obj.get("template-id") or obj.get("templateID"),
                    "name": (obj.get("info") or {}).get("name"),
                    "matched": obj.get("matched-at") or obj.get("host"),
                }
            )
            flags.extend(extract_flags(json.dumps(obj)))
        except Exception:  # noqa: BLE001
            if ln.strip():
                findings.append({"raw": ln[:200]})
    return {
        "cmd": cmd,
        "rc": r.get("rc"),
        "findings": findings[:40],
        "flags_found": list(dict.fromkeys(flags)),
        "stderr_tail": (r.get("stderr") or "")[-400:],
    }


def scanners_available() -> dict[str, bool]:
    return {
        "ffuf": have("ffuf"),
        "sqlmap": have("sqlmap"),
        "nuclei": have("nuclei"),
        "gobuster": have("gobuster"),
        "nmap": have("nmap"),
        "dig": have("dig"),
        "curl": have("curl"),
    }


def scaffold_challenge(slug: str, title: str = "", body: str = "") -> dict[str, Any]:
    root = Path(__file__).resolve().parents[1]
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", slug).strip("-").lower() or "challenge"
    cdir = root / "challenges" / slug
    ndir = root / "notes" / slug
    cdir.mkdir(parents=True, exist_ok=True)
    ndir.mkdir(parents=True, exist_ok=True)
    readme = cdir / "README.md"
    content = body.strip() or f"# {title or slug}\n\nPaste CTFd description below.\n"
    if not readme.exists() or body.strip():
        readme.write_text(content if body.strip() else content)
    triage = ndir / "triage.md"
    if not triage.exists():
        triage.write_text(
            f"# Triage: {title or slug}\n- Signals:\n- Category:\n- Primary skill:\n- Plan:\n  1.\n  2.\n  3.\n"
        )
    (ndir / "trace.md").touch()
    return {"slug": slug, "challenge": str(cdir), "notes": str(ndir), "readme": str(readme)}


def autosolve(
    slug: str,
    target: str | None = None,
    text: str | None = None,
    text_file: str | None = None,
) -> dict[str, Any]:
    """End-to-end first pass: scaffold → parse targets → recon/web-hunt → flags."""
    root = Path(__file__).resolve().parents[1]
    body = text or ""
    if text_file:
        body = Path(text_file).read_text(errors="ignore")
    meta = scaffold_challenge(slug, title=slug, body=body or f"# {slug}\n")
    ndir = Path(meta["notes"])
    targets = extract_targets(body)
    if target:
        if "://" in target:
            targets["urls"] = [target] + [u for u in targets["urls"] if u != target]
        elif re.match(r"^(?:\d{1,3}\.){3}\d{1,3}$", target):
            targets["ips"] = [target] + [i for i in targets["ips"] if i != target]
        else:
            targets["hosts"] = [target] + [h for h in targets["hosts"] if h != target]

    result: dict[str, Any] = {
        "slug": meta["slug"],
        "targets": targets,
        "steps": [],
        "flags_found": [],
    }
    flags: list[str] = []

    def add_flags(xs: list[str]) -> None:
        for f in xs:
            if f not in flags:
                flags.append(f)

    add_flags(extract_flags(body))

    # Peel encoding-looking blobs in challenge text
    for blob in re.findall(r"[A-Za-z0-9+/=_-]{24,}", body or ""):
        try:
            peeled = peel_encodings(blob)
            if peeled.get("flags_found"):
                result["steps"].append({"peel": blob[:40], "flags": peeled["flags_found"]})
                add_flags(peeled["flags_found"])
        except Exception:  # noqa: BLE001
            pass

    # DNS/TXT sometimes holds flags
    for host in targets["hosts"][:5] + targets["ips"][:3]:
        try:
            d = dig_lookup(host)
            result["steps"].append({"dig": host, "txt": d["records"].get("TXT")})
            add_flags(extract_flags(json.dumps(d)))
        except Exception as e:  # noqa: BLE001
            result["steps"].append({"dig": host, "error": str(e)})

    urls = list(targets["urls"])
    for ip in targets["ips"][:3]:
        urls.extend([f"http://{ip}/", f"https://{ip}/"])
    for host in targets["hosts"][:3]:
        if not any(host in u for u in urls):
            urls.extend([f"http://{host}/", f"https://{host}/"])

    nmap_done: set[str] = set()
    for url in urls[:6]:
        try:
            hunt = web_hunt(url)
            result["steps"].append(
                {
                    "web_hunt": url,
                    "summary_flags": hunt.get("flags_found"),
                    "hits": len(hunt.get("hits", [])),
                }
            )
            add_flags(hunt.get("flags_found") or [])
            # sqlmap on likely injection endpoints
            if any(x in url.lower() for x in ("login", "search", "id=", "cat=", "page=", "q=")):
                sm = sqlmap_scan(url, quick=True)
                result["steps"].append(
                    {
                        "sqlmap": url,
                        "interesting": sm.get("interesting"),
                        "flags": sm.get("flags_found"),
                        "error": sm.get("error"),
                    }
                )
                add_flags(sm.get("flags_found") or [])
            host = urlparse(url).hostname
            if host and host not in nmap_done and len(nmap_done) < 2:
                nmap_done.add(host)
                nm = nmap_scan(host, quick=True)
                result["steps"].append({"nmap_quick": host, "rc": nm.get("rc")})
                add_flags(extract_flags(nm.get("stdout") or ""))
        except Exception as e:  # noqa: BLE001
            result["steps"].append({"web_hunt": url, "error": str(e)})

    # if only IP and no urls worked, still quick nmap
    if not urls:
        for ip in targets["ips"][:2]:
            nm = nmap_scan(ip, quick=True)
            result["steps"].append({"nmap_quick": ip, "rc": nm.get("rc")})
            add_flags(extract_flags(nm.get("stdout") or ""))
            result["steps"].append({"http": http_fingerprint(f"http://{ip}/")})

    result["flags_found"] = flags
    (ndir / "autosolve.json").write_text(json.dumps(result, indent=2, default=str))
    trace = ndir / "trace.md"
    with trace.open("a") as f:
        f.write(f"\n## autosolve\nflags={flags}\ntargets={targets}\n")
    if flags:
        for fl in flags:
            try:
                save_flag(meta["slug"], fl, root=root)
            except ValueError:
                continue
    result["next"] = (
        "If no flag: load ctf-triage skill and continue manual exploit loop."
        if not flags
        else "Submit FLAG lines on CTFd."
    )
    return result


def peel_encodings(data: str, rounds: int = 8) -> dict[str, Any]:
    """Peel base64/hex/url encodings; hunt flags at each layer."""
    import base64
    import binascii
    from urllib.parse import unquote_to_bytes

    layers: list[dict[str, Any]] = []
    cur: bytes
    try:
        cur = data.encode() if isinstance(data, str) else data
    except Exception:  # noqa: BLE001
        cur = str(data).encode()

    flags: list[str] = []
    for i in range(rounds):
        text_try = cur.decode("utf-8", errors="replace")
        found = extract_flags(text_try)
        layer = {"i": i, "len": len(cur), "preview": text_try[:120], "flags": found}
        for f in found:
            if f not in flags:
                flags.append(f)
        # try transforms
        nxt = None
        # hex
        hx = re.sub(r"\s+", "", text_try.strip())
        if re.fullmatch(r"[0-9a-fA-F]+", hx) and len(hx) % 2 == 0 and len(hx) >= 8:
            try:
                nxt = binascii.unhexlify(hx)
                layer["transform"] = "hex"
            except Exception:  # noqa: BLE001
                pass
        if nxt is None:
            # base64
            pad = text_try.strip() + ("=" * (-len(text_try.strip()) % 4))
            try:
                nxt = base64.b64decode(pad, validate=False)
                if nxt and nxt != cur:
                    layer["transform"] = "b64"
                else:
                    nxt = None
            except Exception:  # noqa: BLE001
                nxt = None
        if nxt is None:
            try:
                u = unquote_to_bytes(text_try)
                if u != cur and b"%" in cur:
                    nxt = u
                    layer["transform"] = "url"
            except Exception:  # noqa: BLE001
                pass
        layers.append(layer)
        if nxt is None or nxt == cur:
            break
        cur = nxt

    return {"layers": layers, "flags_found": flags, "final_preview": cur[:200].decode("utf-8", errors="replace")}


def whois_lookup(target: str) -> dict[str, Any]:
    target = guard_host(target)
    r = run(["whois", target], timeout=60)
    return {"target": target, **r}



def http_fingerprint(url: str) -> dict[str, Any]:
    url = guard_url(url)
    try:
        from bs4 import BeautifulSoup

        session = guarded_session()
    except ImportError:
        return curl_fetch(url)

    out: dict[str, Any] = {"url": url, "paths": {}}

    def fetch(method: str, req_url: str, **kwargs: Any) -> Any:
        resp, fell_back = request_http(session, method, req_url, **kwargs)
        if fell_back:
            out["tls_verify_fallback"] = True
        return resp

    try:
        resp = fetch("GET", url, timeout=20, allow_redirects=True)
    except Exception as e:  # noqa: BLE001
        return {"url": url, "error": str(e)}

    out["status"] = resp.status_code
    out["final_url"] = str(resp.url)
    out["headers"] = dict(resp.headers)
    out["len"] = len(resp.content)
    out["flags_found"] = extract_flags(resp.text)
    soup = BeautifulSoup(resp.text, "html.parser")
    out["title"] = (soup.title.string.strip() if soup.title and soup.title.string else "")
    out["forms"] = []
    for form in soup.find_all("form"):
        out["forms"].append(
            {
                "action": form.get("action"),
                "method": form.get("method", "get"),
                "inputs": [
                    {"name": i.get("name"), "type": i.get("type")}
                    for i in form.find_all("input")
                ],
            }
        )
    out["links"] = sorted(
        {
            urljoin(str(resp.url), a.get("href"))
            for a in soup.find_all("a", href=True)
            if a.get("href")
        }
    )[:80]

    base = f"{urlparse(str(resp.url)).scheme}://{urlparse(str(resp.url)).netloc}"
    for path in (
        "/robots.txt",
        "/sitemap.xml",
        "/.git/HEAD",
        "/flag",
        "/flag.txt",
        "/.env",
        "/admin",
        "/login",
        "/api",
        "/api/v1",
        "/console",
        "/debug",
        "/swagger",
        "/graphql",
    ):
        try:
            r = fetch("GET", base + path, timeout=10, allow_redirects=False)
            if r.status_code < 500:
                out["paths"][path] = {
                    "status": r.status_code,
                    "len": len(r.content),
                    "flags": extract_flags(r.text),
                    "snippet": r.text[:300],
                }
        except Exception:  # noqa: BLE001
            continue
    return out


def recon(target: str) -> dict[str, Any]:
    """Workshop-aligned recon: dig + nmap + http if looks like host."""
    result: dict[str, Any] = {"target": target}
    if "://" in target:
        target = guard_url(target)
        result["target"] = target
        host = urlparse(target).hostname or ""
        if not host:
            raise ValueError("url is missing a host")
        result["http"] = http_fingerprint(target)
    else:
        host = guard_host(target)
        result["target"] = host
        result["http_http"] = http_fingerprint(f"http://{host}")
        result["http_https"] = http_fingerprint(f"https://{host}")

    result["dns"] = dig_lookup(host)
    result["nmap"] = nmap_scan(host, full=False)
    # harvest flags from all text
    blob = json.dumps(result)
    result["all_flags"] = extract_flags(blob)
    return result


def save_flag(challenge: str, flag: str, root: Path | None = None) -> None:
    challenge = guard_line(challenge, "challenge")
    flag = guard_line(flag, "flag")
    root = root or Path(__file__).resolve().parents[1]
    ledger = root / "flags" / "FOUND.md"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    line = f"- {challenge}: {flag}\n"
    existing = ledger.read_text() if ledger.exists() else "# Flags found\n\n"
    if flag not in existing:
        if not existing.endswith("\n"):
            existing += "\n"
        ledger.write_text(existing + line)
    print(f"FLAG: {flag}")


def main() -> None:
    load_dotenv()
    if not tls_verify_enabled():
        _silence_insecure_warning()

    ap = argparse.ArgumentParser(prog="cypherflag")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("dig", help="DNS lookup (workshop tool)")
    p.add_argument("target")

    p = sub.add_parser("nmap", help="Nmap service scan (workshop tool)")
    p.add_argument("target")
    p.add_argument("--full", action="store_true")
    p.add_argument("--quick", action="store_true")

    p = sub.add_parser("curl", help="Fetch URL")
    p.add_argument("url")
    p.add_argument("-X", "--method", default="GET")
    p.add_argument("-d", "--data", default=None)

    p = sub.add_parser("whois", help="WHOIS")
    p.add_argument("target")

    p = sub.add_parser("http", help="HTTP fingerprint + juicy paths")
    p.add_argument("url")

    p = sub.add_parser("recon", help="Full dig+nmap+http recon")
    p.add_argument("target")

    p = sub.add_parser("extract-flags", help="Extract flags from a file or stdin")
    p.add_argument("path", nargs="?", default="-")

    p = sub.add_parser("save-flag", help="Append flag to flags/FOUND.md and print FLAG:")
    p.add_argument("challenge")
    p.add_argument("flag")

    p = sub.add_parser("new-challenge", help="Scaffold notes/challenges dirs")
    p.add_argument("slug")
    p.add_argument("--title", default="")

    p = sub.add_parser("web-hunt", help="Aggressive path + form probes + ffuf/nuclei")
    p.add_argument("url")

    p = sub.add_parser("ffuf", help="ffuf path fuzz (URL must include FUZZ)")
    p.add_argument("url")
    p.add_argument("--wordlist", default=None)
    p.add_argument("--full", action="store_true")

    p = sub.add_parser("sqlmap", help="sqlmap (CTF targets only)")
    p.add_argument("url")
    p.add_argument("-d", "--data", default=None)
    p.add_argument("--full", action="store_true")

    p = sub.add_parser("nuclei", help="nuclei exposure/misconfig scan")
    p.add_argument("url")
    p.add_argument("--full", action="store_true")

    p = sub.add_parser("scanners", help="Which scanners are installed")

    p = sub.add_parser("extract-targets", help="Pull URLs/IPs/hosts from text")
    p.add_argument("path", nargs="?", default="-")

    p = sub.add_parser("autosolve", help="Autonomous first-pass solve pipeline")
    p.add_argument("--slug", required=True)
    p.add_argument("--target", default=None)
    p.add_argument("--text-file", default=None)
    p.add_argument("--text", default=None)

    p = sub.add_parser("peel", help="Peel base64/hex/url layers; hunt flags")
    p.add_argument("data", nargs="?", default=None)
    p.add_argument("--file", default=None)

    args = ap.parse_args()
    out: Any

    try:
        out = _dispatch(args)
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        raise SystemExit(2) from exc
    if out is None:
        return
    print(json.dumps(out, indent=2, default=str))


def _dispatch(args: argparse.Namespace) -> Any:
    if args.cmd == "dig":
        return dig_lookup(args.target)
    if args.cmd == "nmap":
        return nmap_scan(args.target, full=args.full, quick=args.quick)
    if args.cmd == "curl":
        return curl_fetch(args.url, method=args.method, data=args.data)
    if args.cmd == "whois":
        return whois_lookup(args.target)
    if args.cmd == "http":
        return http_fingerprint(args.url)
    if args.cmd == "recon":
        return recon(args.target)
    if args.cmd == "web-hunt":
        return web_hunt(args.url)
    if args.cmd == "ffuf":
        return ffuf_scan(args.url, wordlist=args.wordlist, quick=not args.full)
    if args.cmd == "sqlmap":
        return sqlmap_scan(args.url, data=args.data, quick=not args.full)
    if args.cmd == "nuclei":
        return nuclei_scan(args.url, quick=not args.full)
    if args.cmd == "scanners":
        return scanners_available()
    if args.cmd == "peel":
        raw = args.data
        if args.file:
            raw = Path(args.file).read_text(errors="ignore")
        if raw is None:
            raw = sys.stdin.read()
        return peel_encodings(raw)
    if args.cmd == "extract-targets":
        text = sys.stdin.read() if args.path == "-" else Path(args.path).read_text(errors="ignore")
        return extract_targets(text)
    if args.cmd == "autosolve":
        return autosolve(
            slug=args.slug,
            target=args.target,
            text=args.text,
            text_file=args.text_file,
        )
    if args.cmd == "extract-flags":
        text = sys.stdin.read() if args.path == "-" else Path(args.path).read_text(errors="ignore")
        return {"flags": extract_flags(text)}
    if args.cmd == "save-flag":
        save_flag(args.challenge, args.flag)
        return None
    if args.cmd == "new-challenge":
        return scaffold_challenge(args.slug, title=args.title)
    raise ValueError(f"unknown command: {args.cmd}")


if __name__ == "__main__":
    main()
