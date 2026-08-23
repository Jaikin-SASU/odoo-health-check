#!/usr/bin/env bash
# Initialise le dépôt local et le publie sur l'organisation Jaikin-SASU.
# Rien n'est poussé sans confirmation explicite.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

ORG="Jaikin-SASU"
REPO="odoo-health-check"
SLUG="$ORG/$REPO"

echo "==> 1/6 Contexte"
echo "    dossier : $HERE"
echo "    cible   : github.com/$SLUG"

echo "==> 2/6 Vérification de l'outillage"
command -v gh  >/dev/null || { echo "    !! gh absent"; exit 1; }
command -v git >/dev/null || { echo "    !! git absent"; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "    !! gh non authentifié : lancez 'gh auth login'"; exit 1; }
echo "    OK — compte $(gh api user --jq .login)"

echo "==> 3/6 Garde-fou : le dépôt existe-t-il déjà ?"
if gh repo view "$SLUG" >/dev/null 2>&1; then
  echo "    Le dépôt $SLUG existe déjà — il sera utilisé comme distant."
  CREATE=no
else
  echo "    $SLUG n'existe pas encore."
  CREATE=yes
fi

echo "==> 4/6 Dépôt local"
if [ ! -d .git ]; then
  git init -q -b main
  echo "    dépôt initialisé (branche main)"
else
  echo "    dépôt déjà initialisé"
fi
# Ne jamais versionner les artefacts de build ni l'environnement virtuel.
grep -q '^\.venv/' .gitignore 2>/dev/null || printf '.venv/\n' >> .gitignore
git add -A
if git diff --cached --quiet; then
  echo "    rien à valider"
else
  git -c user.name="${GIT_AUTHOR_NAME:-Victor Gless-Krumhorn}" \
      -c user.email="${GIT_AUTHOR_EMAIL:-victor@jaikin.eu}" \
      commit -q -m "Audit d'instance Odoo : indexabilité, exposition et sécurité

Outil en ligne de commande sans dépendance, extrait de notre pratique
d'intégration Odoo. Vérifie notamment le piège d'indexabilité introduit
par le champ « Nom de domaine » des paramètres du site.

48 tests, 96 % de couverture."
  echo "    commit créé"
fi

echo "==> 5/6 Publication"
if [ -t 0 ]; then
  read -r -p "    Publier $SLUG en dépôt PUBLIC ? [oui/NON] " go
else
  go="${PUSH_GITHUB:-non}"; [ "$go" = "1" ] && go=oui
  echo "    mode non interactif — PUSH_GITHUB=${PUSH_GITHUB:-0}"
fi
if [ "$go" != "oui" ]; then
  echo "    Ignoré — le dépôt local reste en place."
  echo "    Pour publier : PUSH_GITHUB=1 bash $HERE/push-github.sh"
  exit 0
fi
if [ "$CREATE" = "yes" ]; then
  gh repo create "$SLUG" --public --source=. --remote=origin \
     --description "Audite une instance Odoo publique : indexabilité, exposition du gestionnaire de bases, en-têtes de sécurité et version." \
     --push
else
  git remote get-url origin >/dev/null 2>&1 || git remote add origin "git@github.com:$SLUG.git"
  git push -u origin main
fi

echo "==> 6/6 Finitions"
gh repo edit "$SLUG" --homepage "https://jaikin.eu" \
  --add-topic odoo --add-topic seo --add-topic audit \
  --add-topic security --add-topic python --add-topic cli 2>/dev/null || true

echo
echo "===================== RÉCAPITULATIF ====================="
curl -s -o /dev/null -w " github.com/$SLUG -> HTTP %{http_code}\n" "https://github.com/$SLUG"
echo " Étape suivante : bash $HERE/publish.sh  (PyPI + Docker)"
echo " Puis Read the Docs : https://readthedocs.org/dashboard/import/"
echo "========================================================="
