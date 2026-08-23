"""Reconnaissance d'une instance Odoo et de sa version, à partir d'un instantané."""

import re
from typing import Optional

from .models import Snapshot

#: Signatures fiables. Le simple mot « Odoo » dans le texte n'en est pas une :
#: n'importe quelle page peut parler d'Odoo sans en être une.
_GENERATOR = re.compile(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']Odoo', re.I)
_WEB_STATIC = re.compile(r'["\'](?:https?://[^"\']+)?/web/static/', re.I)
_WEB_ASSETS = re.compile(r'["\'](?:https?://[^"\']+)?/web/assets/', re.I)
_SESSION_COOKIE = re.compile(r'\bsession_id=', re.I)
_ODOO_JS = re.compile(r'odoo\.define\s*\(|/web/webclient/', re.I)

#: Ex. /web/assets/17.0-abc123/web.assets_common.css  ou  /web/assets/saas-16.4-x/…
_VERSION_IN_ASSETS = re.compile(r'/web/assets/(saas[-~]\d+\.\d+|\d+\.\d+)[-~/]', re.I)


def detect_odoo(snapshot: Snapshot) -> bool:
    """Vrai si l'instantané présente au moins une signature technique d'Odoo."""
    if _GENERATOR.search(snapshot.body):
        return True
    if _WEB_STATIC.search(snapshot.body) or _WEB_ASSETS.search(snapshot.body):
        return True
    if _ODOO_JS.search(snapshot.body):
        return True
    if _SESSION_COOKIE.search(snapshot.header("Set-Cookie")):
        return True
    return False


def detect_version(snapshot: Snapshot) -> Optional[str]:
    """Version lue dans le chemin des assets, ou None si elle n'y figure pas."""
    match = _VERSION_IN_ASSETS.search(snapshot.body)
    if not match:
        return None
    return match.group(1).replace("~", "-").lower()
