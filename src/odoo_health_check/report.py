"""Rendu du rapport, en texte lisible ou en JSON."""

import json

from .models import Report, Status

_MARK = {Status.OK: "[ OK ]", Status.INFO: "[INFO]",
         Status.WARN: "[WARN]", Status.FAIL: "[FAIL]"}


def render_text(report: Report) -> str:
    lines = ["", "Audit Odoo — %s" % report.target, "=" * 60]
    for finding in report.findings:
        lines.append("%s %-22s %s" % (_MARK[finding.status], finding.check, finding.message))
        if finding.detail:
            lines.append("       %s" % finding.detail)
    lines += [
        "-" * 60,
        "Bilan : %d OK, %d info, %d avertissement(s), %d échec(s) — statut global %s"
        % (report.count(Status.OK), report.count(Status.INFO),
           report.count(Status.WARN), report.count(Status.FAIL),
           report.worst_status.value),
        "",
    ]
    return "\n".join(lines)


def render_json(report: Report) -> str:
    payload = {
        "target": report.target,
        "findings": [
            {"check": f.check, "status": f.status.value,
             "message": f.message, "detail": f.detail}
            for f in report.findings
        ],
        "summary": {
            "worst_status": report.worst_status.value,
            "ok": report.count(Status.OK),
            "info": report.count(Status.INFO),
            "warn": report.count(Status.WARN),
            "fail": report.count(Status.FAIL),
        },
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)
