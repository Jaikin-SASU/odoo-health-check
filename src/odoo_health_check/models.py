"""Structures de données immuables du rapport d'audit."""

from dataclasses import dataclass, replace
from enum import Enum
from typing import Mapping, Optional, Tuple


class Status(str, Enum):
    """Gravité d'un constat, du plus bénin au plus sérieux."""

    OK = "OK"
    INFO = "INFO"
    WARN = "WARN"
    FAIL = "FAIL"


#: Ordre de gravité croissante, utilisé pour calculer le pire statut d'un rapport.
SEVERITY_ORDER: Tuple[Status, ...] = (Status.OK, Status.INFO, Status.WARN, Status.FAIL)


@dataclass(frozen=True)
class Snapshot:
    """Ce qui a été récupéré du réseau. Aucune logique, uniquement des faits."""

    url: str
    status_code: int
    headers: Mapping[str, str]
    body: str
    robots_txt: Optional[str] = None
    sitemap_status: Optional[int] = None
    db_manager_status: Optional[int] = None
    elapsed_ms: Optional[int] = None

    def header(self, name: str) -> str:
        """Lit un en-tête sans se soucier de la casse."""
        target = name.lower()
        for key, value in self.headers.items():
            if key.lower() == target:
                return value
        return ""


@dataclass(frozen=True)
class Finding:
    """Un constat unitaire."""

    check: str
    status: Status
    message: str
    detail: str = ""


@dataclass(frozen=True)
class Report:
    """Rapport complet. Immuable : `with_finding` renvoie une nouvelle instance."""

    target: str
    findings: Tuple[Finding, ...] = ()

    def with_finding(self, finding: Finding) -> "Report":
        return replace(self, findings=self.findings + (finding,))

    def with_findings(self, findings: Tuple[Finding, ...]) -> "Report":
        return replace(self, findings=self.findings + tuple(findings))

    @property
    def worst_status(self) -> Status:
        worst = Status.OK
        for finding in self.findings:
            if SEVERITY_ORDER.index(finding.status) > SEVERITY_ORDER.index(worst):
                worst = finding.status
        return worst

    def count(self, status: Status) -> int:
        return sum(1 for finding in self.findings if finding.status is status)
