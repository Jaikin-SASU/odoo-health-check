"""Assemble les vérifications en un rapport."""

from .checks import (
    check_database_manager, check_https, check_indexability,
    check_security_headers, check_sitemap, check_version_disclosure,
)
from .detect import detect_odoo, detect_version
from .models import Finding, Report, Snapshot, Status


def audit(snapshot: Snapshot) -> Report:
    """Construit le rapport complet à partir d'un instantané déjà récupéré."""
    is_odoo = detect_odoo(snapshot)
    version = detect_version(snapshot)

    report = Report(target=snapshot.url).with_finding(
        Finding("detection", Status.OK if is_odoo else Status.WARN,
                "Instance Odoo détectée." if is_odoo
                else "Aucune signature Odoo trouvée — les résultats peuvent être hors sujet.")
    )
    return report.with_findings((
        check_version_disclosure(snapshot, version),
        check_indexability(snapshot),
        check_database_manager(snapshot),
        check_https(snapshot),
        check_security_headers(snapshot),
        check_sitemap(snapshot),
    ))
