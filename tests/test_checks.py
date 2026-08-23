from odoo_health_check.checks import (
    check_database_manager, check_https, check_indexability,
    check_security_headers, check_sitemap, check_version_disclosure,
)
from odoo_health_check.models import Snapshot, Status


def snap(**kw):
    base = dict(url="https://x.test/", status_code=200, headers={}, body="")
    base.update(kw)
    return Snapshot(**base)


class TestIndexability:
    """Le piège Odoo : un domaine personnalisé rend le sous-domaine .odoo.com noindex."""

    def test_robots_bloquant_est_un_echec(self):
        f = check_indexability(snap(robots_txt="User-agent: *\nDisallow: /"))
        assert f.status is Status.FAIL

    def test_meta_noindex_est_un_echec(self):
        f = check_indexability(snap(body='<meta name="robots" content="noindex"/>'))
        assert f.status is Status.FAIL

    def test_x_robots_tag_noindex_est_un_echec(self):
        f = check_indexability(snap(headers={"X-Robots-Tag": "noindex"}))
        assert f.status is Status.FAIL

    def test_robots_ouvert_est_ok(self):
        f = check_indexability(snap(robots_txt="User-agent: *\nSitemap: https://x.test/sitemap.xml"))
        assert f.status is Status.OK

    def test_disallow_partiel_ne_bloque_pas(self):
        f = check_indexability(snap(robots_txt="User-agent: *\nDisallow: /web/login"))
        assert f.status is Status.OK


class TestDatabaseManager:
    def test_manager_accessible_est_un_echec_critique(self):
        f = check_database_manager(snap(db_manager_status=200))
        assert f.status is Status.FAIL

    def test_manager_protege_est_ok(self):
        assert check_database_manager(snap(db_manager_status=403)).status is Status.OK

    def test_non_teste_est_informatif(self):
        assert check_database_manager(snap(db_manager_status=None)).status is Status.INFO


class TestHttps:
    def test_http_simple_est_un_echec(self):
        assert check_https(snap(url="http://x.test/")).status is Status.FAIL

    def test_https_sans_hsts_avertit(self):
        assert check_https(snap(url="https://x.test/")).status is Status.WARN

    def test_https_avec_hsts_est_ok(self):
        f = check_https(snap(url="https://x.test/", headers={"Strict-Transport-Security": "max-age=31536000"}))
        assert f.status is Status.OK


class TestSecurityHeaders:
    def test_aucun_en_tete_avertit(self):
        assert check_security_headers(snap()).status is Status.WARN

    def test_tous_les_en_tetes_ok(self):
        f = check_security_headers(snap(headers={
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }))
        assert f.status is Status.OK


class TestSitemap:
    def test_sitemap_present_est_ok(self):
        assert check_sitemap(snap(sitemap_status=200)).status is Status.OK

    def test_sitemap_absent_avertit(self):
        assert check_sitemap(snap(sitemap_status=404)).status is Status.WARN


class TestVersionDisclosure:
    def test_version_ancienne_avertit(self):
        assert check_version_disclosure(snap(), "14.0").status is Status.WARN

    def test_version_recente_est_informative(self):
        assert check_version_disclosure(snap(), "18.0").status is Status.INFO

    def test_version_inconnue_est_informative(self):
        assert check_version_disclosure(snap(), None).status is Status.INFO
