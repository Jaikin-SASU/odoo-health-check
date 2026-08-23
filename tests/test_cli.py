import json

import pytest

from odoo_health_check import cli
from odoo_health_check.http import FetchError
from odoo_health_check.models import Snapshot


def fake_snapshot(**kw):
    base = dict(url="https://x.odoo.com/", status_code=200, headers={},
                body='<meta name="generator" content="Odoo"/>')
    base.update(kw)
    return Snapshot(**base)


class TestCli:
    def test_sortie_zero_quand_tout_va_bien(self, monkeypatch, capsys):
        monkeypatch.setattr(cli, "fetch", lambda *a, **k: fake_snapshot(
            url="https://x.odoo.com/",
            headers={"Strict-Transport-Security": "max-age=1", "X-Content-Type-Options": "nosniff",
                     "X-Frame-Options": "SAMEORIGIN", "Content-Security-Policy": "default-src 'self'",
                     "Referrer-Policy": "no-referrer"},
            robots_txt="User-agent: *", sitemap_status=200, db_manager_status=403))
        assert cli.main(["x.odoo.com"]) == 0

    def test_sortie_un_quand_indexation_bloquee(self, monkeypatch, capsys):
        monkeypatch.setattr(cli, "fetch", lambda *a, **k: fake_snapshot(
            robots_txt="User-agent: *\nDisallow: /"))
        assert cli.main(["x.odoo.com"]) == 1
        assert "indexabilite" in capsys.readouterr().out

    def test_mode_json(self, monkeypatch, capsys):
        monkeypatch.setattr(cli, "fetch", lambda *a, **k: fake_snapshot())
        cli.main(["x.odoo.com", "--json"])
        assert json.loads(capsys.readouterr().out)["target"] == "https://x.odoo.com/"

    def test_erreur_reseau_renvoie_deux(self, monkeypatch, capsys):
        def boom(*a, **k):
            raise FetchError("injoignable")
        monkeypatch.setattr(cli, "fetch", boom)
        assert cli.main(["x.odoo.com"]) == 2

    def test_mode_strict_echoue_sur_avertissement(self, monkeypatch):
        monkeypatch.setattr(cli, "fetch", lambda *a, **k: fake_snapshot(
            url="https://x.odoo.com/", robots_txt="User-agent: *",
            sitemap_status=200, db_manager_status=403))
        assert cli.main(["x.odoo.com", "--strict"]) == 1
