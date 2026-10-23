"""Safety and behavior tests for the CypherFlag CLI. No external hosts."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_cypherflag():
    spec = importlib.util.spec_from_file_location(
        "cypherflag", ROOT / "tools" / "cypherflag.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


CF = load_cypherflag()


class QuietHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:  # noqa: A003
        return


def serve(handler: type[BaseHTTPRequestHandler]) -> tuple[ThreadingHTTPServer, int]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, int(server.server_address[1])


def stop(server: ThreadingHTTPServer) -> None:
    server.shutdown()
    server.server_close()


class FlagPage(QuietHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path != "/":
            self.send_response(404)
            self.end_headers()
            return
        body = (
            b"<html><head><title>Fixture</title></head>"
            b"<body>KLCTF{local_demo_not_a_real_flag}</body></html>"
        )
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class MetadataRedirect(QuietHandler):
    def do_GET(self) -> None:  # noqa: N802
        self.send_response(302)
        self.send_header("Location", "http://169.254.169.254/latest/meta-data/")
        self.end_headers()


class SafetyTests(unittest.TestCase):
    def test_extract_and_peel_roundtrip(self) -> None:
        import base64

        flag = "KLCTF{local_demo_not_a_real_flag}"
        blob = base64.b64encode(flag.encode()).decode()
        peeled = CF.peel_encodings(blob)
        self.assertIn(flag, peeled["flags_found"])
        self.assertEqual(CF.extract_flags(f"status FLAG: {flag}"), [flag])

    def test_rejects_non_http_schemes_and_flag_injection(self) -> None:
        with self.assertRaises(ValueError):
            CF.guard_url("file:///etc/passwd")
        with self.assertRaises(ValueError):
            CF.guard_url("http://169.254.169.254/latest/meta-data/")
        with self.assertRaises(ValueError):
            CF.guard_url("http://2852039166/")
        with self.assertRaises(ValueError):
            CF.guard_host("-oN")
        with self.assertRaises(ValueError):
            CF.guard_host("@8.8.8.8")
        with self.assertRaises(ValueError):
            CF.guard_method("-o")
        with self.assertRaises(ValueError):
            CF.guard_data("@/etc/passwd")

    def test_metadata_opt_in(self) -> None:
        previous = os.environ.get("CYPHERFLAG_ALLOW_METADATA")
        os.environ["CYPHERFLAG_ALLOW_METADATA"] = "1"
        try:
            self.assertEqual(
                CF.guard_url("http://169.254.169.254/"),
                "http://169.254.169.254/",
            )
        finally:
            if previous is None:
                os.environ.pop("CYPHERFLAG_ALLOW_METADATA", None)
            else:
                os.environ["CYPHERFLAG_ALLOW_METADATA"] = previous

    def test_dotenv_cannot_override_path(self) -> None:
        path = ROOT / ".env"
        self.assertFalse(path.exists())
        previous_tls = os.environ.get("CYPHERFLAG_TLS_VERIFY")
        previous_path = os.environ["PATH"]
        os.environ.pop("CYPHERFLAG_TLS_VERIFY", None)
        path.write_text("PATH=/tmp/not-a-real-bin\nCYPHERFLAG_TLS_VERIFY=0\n", encoding="utf-8")
        try:
            CF.load_dotenv()
            self.assertEqual(os.environ["PATH"], previous_path)
            self.assertEqual(os.environ.get("CYPHERFLAG_TLS_VERIFY"), "0")
        finally:
            path.unlink(missing_ok=True)
            if previous_tls is None:
                os.environ.pop("CYPHERFLAG_TLS_VERIFY", None)
            else:
                os.environ["CYPHERFLAG_TLS_VERIFY"] = previous_tls

    def test_cli_blocks_unsafe_targets(self) -> None:
        cli = ["python3", str(ROOT / "tools" / "cypherflag.py")]
        blocked = [
            cli + ["curl", "file:///etc/passwd"],
            cli + ["curl", "http://169.254.169.254/"],
            cli + ["nmap", "--", "-oN"],
            cli + ["curl", "--method=-o", "http://127.0.0.1/"],
        ]
        for cmd in blocked:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 2, cmd)
            payload = json.loads(result.stdout)
            self.assertIn("error", payload)

    def test_scanners_command_is_json(self) -> None:
        result = subprocess.run(
            ["python3", str(ROOT / "tools" / "cypherflag.py"), "scanners"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(result.stdout)
        self.assertIn("curl", data)
        self.assertTrue(data["curl"])

    def test_local_http_fingerprint_finds_flag(self) -> None:
        server, port = serve(FlagPage)
        try:
            out = CF.http_fingerprint(f"http://127.0.0.1:{port}/")
        finally:
            stop(server)
        self.assertEqual(out["status"], 200)
        self.assertEqual(out["title"], "Fixture")
        self.assertIn("KLCTF{local_demo_not_a_real_flag}", out["flags_found"])

    def test_curl_fetch_local_http(self) -> None:
        server, port = serve(FlagPage)
        try:
            out = CF.curl_fetch(f"http://127.0.0.1:{port}/")
        finally:
            stop(server)
        self.assertEqual(out["method"], "GET")
        self.assertIn("KLCTF{local_demo_not_a_real_flag}", out["flags_found"])

    def test_local_web_hunt_still_finds_flag(self) -> None:
        server, port = serve(FlagPage)
        try:
            out = CF.web_hunt(f"http://127.0.0.1:{port}/")
        finally:
            stop(server)
        self.assertIn("KLCTF{local_demo_not_a_real_flag}", out.get("flags_found") or [])
        self.assertNotIn("error", out)

    def test_metadata_redirect_is_not_followed(self) -> None:
        server, port = serve(MetadataRedirect)
        try:
            out = CF.http_fingerprint(f"http://127.0.0.1:{port}/")
        finally:
            stop(server)
        self.assertIn("error", out)
        self.assertIn("metadata", out["error"])

    def test_save_flag_rejects_ledger_injection(self) -> None:
        with self.assertRaises(ValueError):
            CF.save_flag("ok\n- injected: no", "KLCTF{nope}", root=ROOT)

    def test_missing_scanners_still_reject_bad_urls(self) -> None:
        with self.assertRaises(ValueError):
            CF.ffuf_scan("file:///tmp/FUZZ")
        with self.assertRaises(ValueError):
            CF.sqlmap_scan("http://169.254.169.254/")
        with self.assertRaises(ValueError):
            CF.nuclei_scan("javascript:alert(1)")

    def test_solve_script_parses_and_doctor_runs(self) -> None:
        parsed = subprocess.run(
            ["bash", "-n", str(ROOT / "scripts" / "solve.sh")],
            check=False,
        )
        self.assertEqual(parsed.returncode, 0)
        usage = subprocess.run(
            ["bash", str(ROOT / "scripts" / "solve.sh")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(usage.returncode, 2)
        doctor = subprocess.run(
            ["bash", str(ROOT / "scripts" / "solve.sh"), "doctor"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(doctor.returncode, 0, doctor.stderr)
        self.assertIn("cypherflag", doctor.stdout)


if __name__ == "__main__":
    unittest.main()
