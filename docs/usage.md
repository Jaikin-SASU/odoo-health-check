# Utilisation

## Ligne de commande

```bash
odoo-health-check exemple.odoo.com
odoo-health-check exemple.odoo.com --json
odoo-health-check exemple.odoo.com --strict
odoo-health-check exemple.odoo.com --timeout 30 --insecure
```

## Codes de sortie

| Code | Signification |
|---|---|
| `0` | Aucun échec |
| `1` | Au moins un `FAIL` (ou un `WARN` avec `--strict`) |
| `2` | Cible injoignable |

## En intégration continue

```yaml
- name: Audit de l'instance
  run: |
    pip install odoo-health-check
    odoo-health-check "$ODOO_URL" --strict
```

## Comme bibliothèque

```python
from odoo_health_check.audit import audit
from odoo_health_check.http import fetch
from odoo_health_check.report import render_json

print(render_json(audit(fetch("exemple.odoo.com"))))
```

Les vérifications de `odoo_health_check.checks` sont des fonctions pures qui
prennent un `Snapshot` : elles se testent sans accès réseau.
