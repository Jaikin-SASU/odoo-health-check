# Journal des modifications

Le format suit [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/)
et le versionnage [SemVer](https://semver.org/lang/fr/).

## [0.1.2] — 2026-08-23

### Corrigé
- Nom du dépôt Docker Hub : `jaikinsasu/odoo-health-check`. Les versions
  précédentes documentaient une commande `docker run` qui ne fonctionnait pas.

### Ajouté
- Intégration continue : tests sur Python 3.9 à 3.13, construction du paquet,
  construction de l'image Docker et vérification qu'elle ne tourne pas en root.
- Badges d'état dans le README.

## [0.1.1] — 2026-08-23

### Corrigé
- Nom du dépôt Docker Hub dans la documentation
  (`jaikinsasu/odoo-health-check`).

## [0.1.0] — 2026-08-23

### Ajouté
- Vérification `indexabilite` : `robots.txt`, balise `meta robots` et en-tête
  `X-Robots-Tag`. Détecte le cas où un nom de domaine configuré dans les
  paramètres du site rend tout autre hôte non indexable.
- Vérification `gestionnaire_bases` : `/web/database/manager` exposé.
- Vérifications `https`, `en_tetes_securite`, `sitemap`, `version`.
- Détection d'instance Odoo par signature technique et lecture de la version
  dans le chemin des assets.
- Sorties texte et JSON, codes de sortie exploitables en intégration continue,
  option `--strict`.
- Image Docker, exécutée sous un utilisateur non privilégié.

[0.1.1]: https://github.com/Jaikin-SASU/odoo-health-check/releases/tag/v0.1.1
[0.1.0]: https://github.com/Jaikin-SASU/odoo-health-check/releases/tag/v0.1.0
