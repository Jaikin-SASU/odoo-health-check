"""Couche réseau, isolée pour que les vérifications restent testables sans Internet."""

import ssl
import time
import urllib.error
import urllib.request
from typing import Optional
from urllib.parse import urljoin, urlparse

from .models import Snapshot

USER_AGENT = "odoo-health-check/0.1 (+https://jaikin.eu)"
_MAX_BODY_BYTES = 2_000_000


class FetchError(RuntimeError):
    """Le serveur est injoignable ou la cible n'est pas exploitable."""


def normalize_url(raw: str) -> str:
    """Complète et valide une URL saisie par l'utilisateur.

    Lève FetchError si l'entrée n'est pas une adresse http(s) exploitable —
    on ne fait jamais confiance à une saisie sans la valider.
    """
    candidate = (raw or "").strip()
    if not candidate:
        raise FetchError("Aucune URL fournie.")
    if "://" not in candidate:
        candidate = "https://" + candidate
    parsed = urlparse(candidate)
    if parsed.scheme not in ("http", "https"):
        raise FetchError("Seuls http et https sont acceptés (reçu : %s)." % parsed.scheme)
    if not parsed.netloc:
        raise FetchError("URL incomplète : %s" % raw)
    return candidate


def _get(url: str, timeout: float, verify_tls: bool):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    context = None if verify_tls else ssl._create_unverified_context()
    return urllib.request.urlopen(request, timeout=timeout, context=context)


def _status_only(url: str, timeout: float, verify_tls: bool) -> Optional[int]:
    """Code HTTP d'une ressource annexe, sans jamais interrompre l'audit."""
    try:
        with _get(url, timeout, verify_tls) as response:
            return response.getcode()
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception:
        return None


def _read_text(url: str, timeout: float, verify_tls: bool) -> Optional[str]:
    try:
        with _get(url, timeout, verify_tls) as response:
            return response.read(_MAX_BODY_BYTES).decode("utf-8", errors="replace")
    except Exception:
        return None


def fetch(raw_url: str, timeout: float = 15.0, verify_tls: bool = True) -> Snapshot:
    """Rassemble tout ce dont les vérifications ont besoin, en une passe."""
    url = normalize_url(raw_url)
    started = time.time()
    try:
        with _get(url, timeout, verify_tls) as response:
            body = response.read(_MAX_BODY_BYTES).decode("utf-8", errors="replace")
            headers = dict(response.headers.items())
            status_code = response.getcode()
            final_url = response.geturl()
    except urllib.error.HTTPError as exc:
        body = exc.read(_MAX_BODY_BYTES).decode("utf-8", errors="replace") if exc.fp else ""
        headers, status_code, final_url = dict(exc.headers.items()), exc.code, url
    except urllib.error.URLError as exc:
        raise FetchError("Impossible de joindre %s : %s" % (url, exc.reason)) from exc
    except Exception as exc:  # timeout, TLS, DNS…
        raise FetchError("Impossible de joindre %s : %s" % (url, exc)) from exc

    elapsed_ms = int((time.time() - started) * 1000)
    return Snapshot(
        url=final_url,
        status_code=status_code,
        headers=headers,
        body=body,
        robots_txt=_read_text(urljoin(final_url, "/robots.txt"), timeout, verify_tls),
        sitemap_status=_status_only(urljoin(final_url, "/sitemap.xml"), timeout, verify_tls),
        db_manager_status=_status_only(
            urljoin(final_url, "/web/database/manager"), timeout, verify_tls),
        elapsed_ms=elapsed_ms,
    )
