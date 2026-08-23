from odoo_health_check.detect import detect_odoo, detect_version
from odoo_health_check.models import Snapshot


def snap(body="", headers=None, **kw):
    return Snapshot(url="https://x.test/", status_code=200,
                    headers=headers or {}, body=body, **kw)


class TestDetectOdoo:
    def test_reconnait_la_balise_generator(self):
        assert detect_odoo(snap(body='<meta name="generator" content="Odoo"/>')) is True

    def test_reconnait_les_ressources_web_static(self):
        assert detect_odoo(snap(body='<script src="/web/static/lib/x.js"></script>')) is True

    def test_reconnait_le_cookie_de_session(self):
        assert detect_odoo(snap(headers={"Set-Cookie": "session_id=abc; Path=/"})) is True

    def test_ne_confond_pas_avec_un_site_quelconque(self):
        assert detect_odoo(snap(body="<html><body>Bonjour</body></html>")) is False

    def test_le_mot_odoo_dans_le_texte_ne_suffit_pas(self):
        assert detect_odoo(snap(body="<p>Nous adorons Odoo</p>")) is False


class TestDetectVersion:
    def test_extrait_la_version_du_chemin_des_assets(self):
        assert detect_version(snap(body='href="/web/assets/17.0-abc/web.assets.css"')) == "17.0"

    def test_extrait_la_version_saas(self):
        assert detect_version(snap(body='src="/web/assets/saas-16.4-x/a.js"')) == "saas-16.4"

    def test_renvoie_none_quand_absente(self):
        assert detect_version(snap(body="<html></html>")) is None
