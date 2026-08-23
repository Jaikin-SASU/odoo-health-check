"""Vérifications unitaires. Fonctions pures : un instantané entre, un constat sort."""

import re
from typing import Optional, Tuple

from .models import Finding, Snapshot, Status

#: Version majeure la plus ancienne encore raisonnablement maintenue.
OLDEST_SUPPORTED_MAJOR = 16

_DISALLOW_ALL = re.compile(r"^\s*Disallow:\s*/\s*$", re.I | re.M)
_META_NOINDEX = re.compile(r'<meta[^>]+name=["\']robots["\'][^>]*noindex', re.I)

_SECURITY_HEADERS: Tuple[str, ...] = (
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Content-Security-Policy",
    "Referrer-Policy",
)


def check_indexability(snapshot: Snapshot) -> Finding:
    """Le piège Odoo le plus courant.

    Dès qu'un nom de domaine personnalisé est renseigné dans les paramètres du
    site, Odoo sert `Disallow: /` et une balise `noindex` sur tout autre hôte —
    y compris le sous-domaine `.odoo.com` d'origine. Une instance que l'on croit
    référencée peut ainsi être invisible depuis des mois.
    """
    blockers = []
    if snapshot.robots_txt and _DISALLOW_ALL.search(snapshot.robots_txt):
        blockers.append("robots.txt : Disallow: /")
    if _META_NOINDEX.search(snapshot.body):
        blockers.append('balise <meta name="robots" content="noindex">')
    if "noindex" in snapshot.header("X-Robots-Tag").lower():
        blockers.append("en-tête X-Robots-Tag: noindex")

    if blockers:
        return Finding(
            check="indexabilite",
            status=Status.FAIL,
            message="Cette instance est invisible pour les moteurs de recherche.",
            detail=" ; ".join(blockers)
            + ". Cause la plus fréquente : un nom de domaine est renseigné dans"
            " Site web > Configuration alors que l'on consulte un autre hôte.",
        )
    return Finding(
        check="indexabilite",
        status=Status.OK,
        message="Aucun blocage d'indexation détecté.",
    )


def check_database_manager(snapshot: Snapshot) -> Finding:
    """Le gestionnaire de bases exposé permet de lister, dupliquer ou supprimer des bases."""
    if snapshot.db_manager_status is None:
        return Finding("gestionnaire_bases", Status.INFO,
                       "Gestionnaire de bases non vérifié.")
    if snapshot.db_manager_status == 200:
        return Finding(
            check="gestionnaire_bases",
            status=Status.FAIL,
            message="/web/database/manager répond publiquement.",
            detail="Renseignez `list_db = False` et un `admin_passwd` fort dans odoo.conf.",
        )
    return Finding("gestionnaire_bases", Status.OK,
                   "Gestionnaire de bases inaccessible publiquement.",
                   "HTTP %s" % snapshot.db_manager_status)


def check_https(snapshot: Snapshot) -> Finding:
    if not snapshot.url.lower().startswith("https://"):
        return Finding("https", Status.FAIL, "Le site est servi en HTTP simple.",
                       "Les sessions Odoo transitent en clair.")
    if not snapshot.header("Strict-Transport-Security"):
        return Finding("https", Status.WARN, "HTTPS actif mais sans HSTS.",
                       "Ajoutez Strict-Transport-Security.")
    return Finding("https", Status.OK, "HTTPS actif, HSTS présent.")


def check_security_headers(snapshot: Snapshot) -> Finding:
    missing = [h for h in _SECURITY_HEADERS if not snapshot.header(h)]
    if not missing:
        return Finding("en_tetes_securite", Status.OK, "En-têtes de sécurité présents.")
    return Finding("en_tetes_securite", Status.WARN,
                   "%d en-tête(s) de sécurité manquant(s)." % len(missing),
                   ", ".join(missing))


def check_sitemap(snapshot: Snapshot) -> Finding:
    if snapshot.sitemap_status is None:
        return Finding("sitemap", Status.INFO, "Sitemap non vérifié.")
    if snapshot.sitemap_status == 200:
        return Finding("sitemap", Status.OK, "/sitemap.xml est servi.")
    return Finding("sitemap", Status.WARN, "/sitemap.xml introuvable.",
                   "HTTP %s — le module Site web le génère normalement."
                   % snapshot.sitemap_status)


def check_version_disclosure(snapshot: Snapshot, version: Optional[str]) -> Finding:
    if not version:
        return Finding("version", Status.INFO, "Version non déterminée.")
    major = _major_of(version)
    if major is not None and major < OLDEST_SUPPORTED_MAJOR:
        return Finding("version", Status.WARN,
                       "Version %s : hors support courant." % version,
                       "Les correctifs de sécurité ne sont plus garantis.")
    return Finding("version", Status.INFO, "Version détectée : %s." % version)


def _major_of(version: str) -> Optional[int]:
    match = re.search(r"(\d+)\.", version)
    return int(match.group(1)) if match else None
