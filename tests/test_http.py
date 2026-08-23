import pytest

from odoo_health_check.http import FetchError, normalize_url


class TestNormalizeUrl:
    def test_ajoute_https_par_defaut(self):
        assert normalize_url("exemple.odoo.com") == "https://exemple.odoo.com"

    def test_conserve_une_url_complete(self):
        assert normalize_url("http://x.test/a") == "http://x.test/a"

    def test_ignore_les_espaces(self):
        assert normalize_url("  x.test  ") == "https://x.test"

    @pytest.mark.parametrize("bad", ["", "   ", "ftp://x.test", "file:///etc/passwd", "https://"])
    def test_refuse_les_entrees_invalides(self, bad):
        with pytest.raises(FetchError):
            normalize_url(bad)
