# Publier le paquet — mode d'emploi

## ⚠️ Le token PyPI ne doit jamais passer par la session Claude

Une commande lancée avec `! …` est écrite dans la conversation. **Ne collez donc
jamais un token dans une commande `!`.** Créez le fichier d'identifiants depuis
votre propre terminal (Terminal.app, iTerm…), une seule fois.

## 1. Créer le token

Sur https://pypi.org/manage/account/token/ → *Add API token*.

Portée : à la première publication le paquet n'existe pas encore, il faut donc un
token « Entire account ». Après la première publication, révoquez-le et
recréez-en un limité au projet `odoo-health-check`.

## 2. Enregistrer le token (dans VOTRE terminal, pas via `!`)

```bash
umask 077                       # le fichier ne sera lisible que par vous
cat > ~/.pypirc <<'PYPIRC'
[distutils]
index-servers = pypi

[pypi]
username = __token__
password = COLLEZ_ICI_LE_TOKEN
PYPIRC
chmod 600 ~/.pypirc
```

Vérification (n'affiche pas le token) :

```bash
ls -l ~/.pypirc && grep -c '^password' ~/.pypirc
```

## 3. Publier

Depuis la session Claude, en non interactif :

```bash
PUBLISH_PYPI=1 bash /Users/victor.glesskrumhorn/code/victorwhale/odoo-health-check/publish.sh
```

Le script rejoue les tests et la couverture (bloquants), reconstruit, valide avec
`twine check`, puis publie. Sans `PUBLISH_PYPI=1`, il s'arrête juste avant la
publication — pratique pour une répétition à blanc.

## 4. Docker Hub

Connectez-vous d'abord depuis votre terminal (`docker login`), puis :

```bash
PUBLISH_DOCKER=1 bash /Users/victor.glesskrumhorn/code/victorwhale/odoo-health-check/publish.sh
```

## 5. Dépôt GitHub

```bash
PUSH_GITHUB=1 bash /Users/victor.glesskrumhorn/code/victorwhale/odoo-health-check/push-github.sh
```

## 6. Read the Docs

Une fois le dépôt en ligne : https://readthedocs.org/dashboard/import/ →
importer `Jaikin-SASU/odoo-health-check`. La configuration `.readthedocs.yaml`
et `mkdocs.yml` sont déjà en place, rien d'autre à régler.

## Après la première publication

- Révoquer le token « Entire account », en recréer un limité au projet.
- Vérifier que la fiche affiche bien le lien *Homepage* vers `jaikin.eu` :
  c'est lui qui porte le backlink dofollow.
