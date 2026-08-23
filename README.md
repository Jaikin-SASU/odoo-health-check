# odoo-health-check

[![CI](https://github.com/Jaikin-SASU/odoo-health-check/actions/workflows/ci.yml/badge.svg)](https://github.com/Jaikin-SASU/odoo-health-check/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/odoo-health-check)](https://pypi.org/project/odoo-health-check/)
[![Python](https://img.shields.io/pypi/pyversions/odoo-health-check)](https://pypi.org/project/odoo-health-check/)

Audite une instance Odoo publique en une commande : indexabilité, exposition du
gestionnaire de bases, en-têtes de sécurité, version et sitemap.

```bash
pip install odoo-health-check
odoo-health-check exemple.odoo.com
```

```
Audit Odoo — https://exemple.odoo.com/
============================================================
[ OK ] detection              Instance Odoo détectée.
[INFO] version                Version détectée : 17.0.
[FAIL] indexabilite           Cette instance est invisible pour les moteurs de recherche.
       robots.txt : Disallow: / . Cause la plus fréquente : un nom de domaine est
       renseigné dans Site web > Configuration alors que l'on consulte un autre hôte.
[ OK ] gestionnaire_bases     Gestionnaire de bases inaccessible publiquement.
[WARN] https                  HTTPS actif mais sans HSTS.
[WARN] en_tetes_securite      2 en-tête(s) de sécurité manquant(s).
       Content-Security-Policy, Referrer-Policy
[ OK ] sitemap                /sitemap.xml est servi.
------------------------------------------------------------
Bilan : 3 OK, 1 info, 2 avertissement(s), 1 échec(s) — statut global FAIL
```

## Pourquoi cet outil existe

En auditant des instances Odoo hébergées, un même défaut revenait sans arrêt :
**des sites en ligne depuis des mois, totalement absents de Google**, sans que
personne ne comprenne pourquoi.

La cause est dans le moteur lui-même. Le gabarit `robots` d'Odoo
(`addons/website/views/website_templates.xml`) contient cette condition :

```xml
<t t-if="website.domain and not website._is_indexable_url(url_root)">
Disallow: /
</t>
```

Autrement dit : **dès qu'un nom de domaine est renseigné dans les paramètres du
site, tout autre hôte servant la même base reçoit `Disallow: /` et une balise
`noindex`** — y compris le sous-domaine `.odoo.com` d'origine, y compris une
préproduction, y compris le `www.` si le champ contient la version nue du domaine.
La même condition pilote la balise meta dans le `<head>`.

C'est silencieux, cohérent du point de vue d'Odoo (éviter le contenu dupliqué),
et invisible tant qu'on ne lit pas le `robots.txt` servi par l'hôte exact que
consultent les visiteurs. Cet outil le lit pour vous, avec quelques autres
vérifications qui coûtent une seconde et évitent des semaines de silence.

## Ce qui est vérifié

| Vérification | Ce qu'elle détecte |
|---|---|
| `detection` | Signature technique Odoo (generator, `/web/static/`, `/web/assets/`, cookie de session) |
| `version` | Version lue dans le chemin des assets ; avertit sous la 16.0 |
| `indexabilite` | `Disallow: /`, `<meta robots noindex>`, `X-Robots-Tag: noindex` |
| `gestionnaire_bases` | `/web/database/manager` accessible publiquement |
| `https` | HTTP simple, absence de HSTS |
| `en_tetes_securite` | CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy |
| `sitemap` | `/sitemap.xml` servi ou non |

## Utilisation

```bash
odoo-health-check exemple.odoo.com              # rapport lisible
odoo-health-check exemple.odoo.com --json       # sortie JSON
odoo-health-check exemple.odoo.com --strict     # code de sortie 1 dès un avertissement
odoo-health-check exemple.odoo.com --timeout 30
```

Codes de sortie : `0` conforme, `1` au moins un échec (ou un avertissement en
`--strict`), `2` cible injoignable. Utilisable tel quel dans une intégration continue.

### Docker

```bash
docker run --rm jaikin-sasu/odoo-health-check exemple.odoo.com
```

### Comme bibliothèque

```python
from odoo_health_check.http import fetch
from odoo_health_check.audit import audit

report = audit(fetch("exemple.odoo.com"))
print(report.worst_status, len(report.findings))
```

## Portée et limites

L'outil n'envoie que des requêtes `GET` sur des chemins publics et ne tente
aucune authentification, aucune injection, aucune écriture. Il constate ce
qu'un visiteur — ou un moteur de recherche — voit déjà.

**N'auditez que des instances qui vous appartiennent ou pour lesquelles vous
disposez d'une autorisation écrite.**

La détection de version repose sur le chemin des assets : un reverse proxy qui
réécrit ces URL la rendra muette. Un `FAIL` sur `indexabilite` signifie que le
crawl est interdit, pas qu'une page est désindexée — la désindexation effective
prend des semaines.

## Développement

```bash
git clone https://github.com/Jaikin-SASU/odoo-health-check
cd odoo-health-check
PYTHONPATH=src python -m pytest tests/ -q
```

Aucune dépendance d'exécution : uniquement la bibliothèque standard.

## Auteur

Développé par [JAIKIN](https://jaikin.eu), ESN et agence IA près de Strasbourg —
intelligence artificielle, data, développement sur mesure et intégration Odoo.

Cet outil est extrait de notre pratique d'intégration : les vérifications qu'il
automatise sont celles que nous faisions à la main sur chaque instance livrée.
Nous publions régulièrement nos mesures sur [jaikin.eu](https://jaikin.eu).

## Licence

MIT — voir [LICENSE](LICENSE).
