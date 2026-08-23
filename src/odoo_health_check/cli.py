"""Point d'entrée en ligne de commande."""

import argparse
import sys

from .audit import audit
from .http import FetchError, fetch
from .models import Status
from .report import render_json, render_text

#: Code de sortie 1 dès qu'un échec est constaté : exploitable en intégration continue.
_FAILING = (Status.FAIL,)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="odoo-health-check",
        description="Audite une instance Odoo publique : indexabilité, exposition, "
                    "en-têtes de sécurité et version.",
        epilog="N'auditez que des instances qui vous appartiennent ou pour "
               "lesquelles vous avez une autorisation écrite.",
    )
    parser.add_argument("url", help="URL de l'instance, ex. https://exemple.odoo.com")
    parser.add_argument("--json", action="store_true", help="sortie JSON")
    parser.add_argument("--timeout", type=float, default=15.0, help="délai réseau en secondes")
    parser.add_argument("--insecure", action="store_true",
                        help="ne pas vérifier le certificat TLS")
    parser.add_argument("--strict", action="store_true",
                        help="sortir en erreur dès un avertissement")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        snapshot = fetch(args.url, timeout=args.timeout, verify_tls=not args.insecure)
    except FetchError as exc:
        print("Erreur : %s" % exc, file=sys.stderr)
        return 2

    report = audit(snapshot)
    print(render_json(report) if args.json else render_text(report))

    failing = _FAILING + ((Status.WARN,) if args.strict else ())
    return 1 if report.worst_status in failing else 0


if __name__ == "__main__":
    raise SystemExit(main())
