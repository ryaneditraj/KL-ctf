#!/usr/bin/env python3
"""CypherFlag toolkit — recon + web helpers the agent should call via shell."""
from __future__ import annotations

import argparse
import json
import re
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

BRACE_FLAG_RE = re.compile(r"[A-Za-z0-9_\-]{2,32}\{[^}\n]{3,200}\}")
FLAG_LABEL_RE = re.compile(
    r"(?:FLAG|flag|CTF|ctf|UCSI|ucsi)\s*[:=]\s*(\S{4,160})"
)


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
    out: dict[str, Any] = {"target": target, "records": {}}
    for rtype in ("A", "AAAA", "MX", "TXT", "NS", "CNAME"):
        r = run(["dig", "+short", target, rtype], timeout=30)
        lines = [ln.strip() for ln in r["stdout"].splitlines() if ln.strip()]
        out["records"][rtype] = lines
    any_r = run(["dig", target, "ANY", "+noall", "+answer"], timeout=30)
    out["any_answer"] = any_r["stdout"]
    return out


def nmap_scan(target: str, full: bool = False, quick: bool = False) -> dict[str, Any]:
    if full:
        cmd = ["nmap", "-Pn", "-sV", "-sC", "-T4", "-p-", target]
        timeout = 600
    elif quick:
        cmd = ["nmap", "-Pn", "-T4", "--top-ports", "100", target]
        timeout = 90
    else:
        cmd = ["nmap", "-Pn", "-sV", "-sC", "-T4", "--top-ports", "1000", target]
        timeout = 300
    r = run(cmd, timeout=timeout)
    return {"target": target, "full": full, "quick": quick, **r}



def curl_fetch(url: str, method: str = "GET", data: str | None = None) -> dict[str, Any]:
    cmd = ["curl", "-sS", "-L", "-D", "-", "--max-time", "30", "-X", method]
    if data is not None:
        cmd += ["--data", data]
    cmd.append(url)
    r = run(cmd, timeout=60)
    # Split headers/body on first blank line in stdout (curl -D - interleaves; use -i style)
    # Re-run with -i for cleaner parse
    cmd2 = ["curl", "-sS", "-L", "-i", "--max-time", "30", "-X", method]
    if data is not None:
        cmd2 += ["--data", data]
    cmd2.append(url)
    r2 = run(cmd2, timeout=60)
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
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        return {"error": "requests/bs4 missing", "fallback": curl_fetch(url)}

    session = requests.Session()
    session.headers["User-Agent"] = "CypherFlag/1.0"
    session.verify = False
    out: dict[str, Any] = {"url": url, "hits": [], "flags_found": [], "form_probes": []}
    flags: list[str] = []

    def note_flags(src: str, label: str) -> None:
        for f in extract_flags(src):
            if f not in flags:
                flags.append(f)
                out["hits"].append({"where": label, "flag": f})

    try:
        base_resp = session.get(url, timeout=20, allow_redirects=True)
    except Exception as e:  # noqa: BLE001
        return {"url": url, "error": str(e)}

    note_flags(base_resp.text, "index")
    note_flags(str(base_resp.headers), "headers")
    parsed = urlparse(str(base_resp.url))
    base = f"{parsed.scheme}://{parsed.netloc}"

    for path in load_paths():
        try:
            r = session.get(base + path, timeout=8, allow_redirects=True)
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
    soup = BeautifulSoup(base_resp.text, "lxml")
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
                    r = session.post(action, data=data, timeout=10)
                else:
                    r = session.get(action, params=data, timeout=10)
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

    out["flags_found"] = flags
    return out


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
            save_flag(meta["slug"], fl, root=root)
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
    r = run(["whois", target], timeout=60)
    return {"target": target, **r}



def http_fingerprint(url: str) -> dict[str, Any]:
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        return curl_fetch(url)

    out: dict[str, Any] = {"url": url, "paths": {}}
    session = requests.Session()
    session.headers["User-Agent"] = "CypherFlag/1.0"
    try:
        resp = session.get(url, timeout=20, allow_redirects=True, verify=False)
    except Exception as e:  # noqa: BLE001
        return {"url": url, "error": str(e)}

    out["status"] = resp.status_code
    out["final_url"] = str(resp.url)
    out["headers"] = dict(resp.headers)
    out["len"] = len(resp.content)
    out["flags_found"] = extract_flags(resp.text)
    soup = BeautifulSoup(resp.text, "lxml")
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
            r = session.get(base + path, timeout=10, allow_redirects=False, verify=False)
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
    host = target
    if "://" in target:
        host = urlparse(target).hostname or target
        result["http"] = http_fingerprint(target if "://" in target else f"http://{target}")
    else:
        # try http anyway
        result["http_http"] = http_fingerprint(f"http://{host}")
        result["http_https"] = http_fingerprint(f"https://{host}")

    result["dns"] = dig_lookup(host)
    result["nmap"] = nmap_scan(host, full=False)
    # harvest flags from all text
    blob = json.dumps(result)
    result["all_flags"] = extract_flags(blob)
    return result


def save_flag(challenge: str, flag: str, root: Path | None = None) -> None:
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
    # silence insecure warn for CTF labs
    try:
        import urllib3

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    except Exception:  # noqa: BLE001
        pass

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

    p = sub.add_parser("web-hunt", help="Aggressive path + form probes")
    p.add_argument("url")

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

    if args.cmd == "dig":
        out = dig_lookup(args.target)
    elif args.cmd == "nmap":
        out = nmap_scan(args.target, full=args.full, quick=args.quick)
    elif args.cmd == "curl":
        out = curl_fetch(args.url, method=args.method, data=args.data)
    elif args.cmd == "whois":
        out = whois_lookup(args.target)
    elif args.cmd == "http":
        out = http_fingerprint(args.url)
    elif args.cmd == "recon":
        out = recon(args.target)
    elif args.cmd == "web-hunt":
        out = web_hunt(args.url)
    elif args.cmd == "peel":
        raw = args.data
        if args.file:
            raw = Path(args.file).read_text(errors="ignore")
        if raw is None:
            raw = sys.stdin.read()
        out = peel_encodings(raw)
    elif args.cmd == "extract-targets":
        text = sys.stdin.read() if args.path == "-" else Path(args.path).read_text(errors="ignore")
        out = extract_targets(text)
    elif args.cmd == "autosolve":
        out = autosolve(
            slug=args.slug,
            target=args.target,
            text=args.text,
            text_file=args.text_file,
        )
    elif args.cmd == "extract-flags":
        text = sys.stdin.read() if args.path == "-" else Path(args.path).read_text(errors="ignore")
        out = {"flags": extract_flags(text)}
    elif args.cmd == "save-flag":
        save_flag(args.challenge, args.flag)
        return
    elif args.cmd == "new-challenge":
        out = scaffold_challenge(args.slug, title=args.title)
    else:
        ap.error("unknown")

    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
