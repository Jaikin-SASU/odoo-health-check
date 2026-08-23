from odoo_health_check.models import Finding, Report, Status
from odoo_health_check.report import render_json, render_text


def rep():
    return Report(target="https://x.test/").with_findings((
        Finding("https", Status.OK, "HTTPS actif"),
        Finding("indexabilite", Status.FAIL, "Bloqué par robots.txt", "Disallow: /"),
    ))


class TestReportModel:
    def test_with_finding_ne_mute_pas_l_original(self):
        base = Report(target="https://x.test/")
        enrichi = base.with_finding(Finding("c", Status.OK, "m"))
        assert base.findings == ()
        assert len(enrichi.findings) == 1

    def test_worst_status_retient_le_plus_grave(self):
        assert rep().worst_status is Status.FAIL

    def test_count_par_statut(self):
        assert rep().count(Status.OK) == 1


class TestRendering:
    def test_le_texte_contient_la_cible_et_les_constats(self):
        out = render_text(rep())
        assert "https://x.test/" in out and "indexabilite" in out

    def test_le_json_est_valide_et_structure(self):
        import json
        data = json.loads(render_json(rep()))
        assert data["target"] == "https://x.test/"
        assert len(data["findings"]) == 2
        assert data["summary"]["worst_status"] == "FAIL"
