"""Tests de la couche réseau avec un serveur HTTP local — pas d'accès Internet."""

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from odoo_health_check.http import FetchError, fetch

BODY = b'<meta name="generator" content="Odoo"/><script src="/web/assets/17.0-a/x.js"></script>'


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == "/robots.txt":
            payload = b"User-agent: *\nDisallow: /"
            self.send_response(200)
        elif self.path == "/sitemap.xml":
            payload = b"<urlset/>"
            self.send_response(200)
        elif self.path == "/web/database/manager":
            payload = b"forbidden"
            self.send_response(403)
        elif self.path == "/boom":
            payload = b"nope"
            self.send_response(500)
        else:
            payload = BODY
            self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("X-Robots-Tag", "all")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


@pytest.fixture(scope="module")
def server():
    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield "http://127.0.0.1:%d" % httpd.server_address[1]
    httpd.shutdown()


class TestFetch:
    def test_rassemble_page_robots_sitemap_et_manager(self, server):
        snap = fetch(server, timeout=5)
        assert snap.status_code == 200
        assert "generator" in snap.body
        assert snap.robots_txt.startswith("User-agent")
        assert snap.sitemap_status == 200
        assert snap.db_manager_status == 403
        assert snap.elapsed_ms is not None

    def test_lit_les_en_tetes_sans_casse(self, server):
        assert fetch(server, timeout=5).header("x-robots-tag") == "all"

    def test_une_erreur_http_ne_stoppe_pas_l_audit(self, server):
        assert fetch(server + "/boom", timeout=5).status_code == 500

    def test_hote_injoignable_leve_fetch_error(self):
        with pytest.raises(FetchError):
            fetch("http://127.0.0.1:1/", timeout=1)
