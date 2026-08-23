#!/usr/bin/env bash
# Publie odoo-health-check sur PyPI puis construit et pousse l'image Docker.
#
# Fonctionne dans un terminal interactif ET via `! bash …` (sans TTY).
# Sans TTY, les étapes de publication ne s'exécutent que si on les demande
# explicitement :   PUBLISH_PYPI=1   et/ou   PUBLISH_DOCKER=1
#
# Les identifiants PyPI ne sont JAMAIS passés en argument : twine lit ~/.pypirc
# (ou les variables TWINE_USERNAME / TWINE_PASSWORD si elles sont déjà exportées).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

PKG="odoo-health-check"
VERSION="$(grep -m1 '^version' pyproject.toml | cut -d'"' -f2)"
DOCKER_REPO="${DOCKER_REPO:-jaikin/odoo-health-check}"
VENV="$HERE/.venv"

# Demande une confirmation. Sans TTY, s'appuie sur la variable passée en $2.
confirm () {
  local question="$1" envvar="$2"
  if [ -t 0 ]; then
    read -r -p "    $question [oui/NON] " answer
    [ "$answer" = "oui" ]
  else
    [ "${!envvar:-0}" = "1" ]
  fi
}

echo "==> 1/7 Contexte"
echo "    paquet  : $PKG $VERSION"
echo "    mode    : $([ -t 0 ] && echo 'terminal interactif' || echo 'non interactif (variables requises)')"

echo "==> 2/7 Garde-fou : le nom est-il libre sur PyPI ?"
CODE="$(curl -s -o /dev/null -w '%{http_code}' -m 15 "https://pypi.org/pypi/$PKG/json")"
if [ "$CODE" = "200" ]; then
  echo "    !! $PKG existe déjà sur PyPI."
  confirm "Continuer quand même ?" FORCE_EXISTING || { echo "    Abandon."; exit 1; }
else
  echo "    OK — nom libre (HTTP $CODE)."
fi

echo "==> 3/7 Environnement de build"
[ -d "$VENV" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" install --quiet --upgrade pip build twine pytest coverage 2>/dev/null

echo "==> 4/7 Tests + couverture (bloquant)"
PYTHONPATH="$HERE/src" "$VENV/bin/python" -m coverage run --source="$HERE/src/odoo_health_check" -m pytest tests/ -q
PYTHONPATH="$HERE/src" "$VENV/bin/python" -m coverage report --fail-under=80

echo "==> 5/7 Construction"
rm -rf "$HERE/dist"
"$VENV/bin/python" -m build --outdir "$HERE/dist" >/dev/null
"$VENV/bin/python" -m twine check "$HERE"/dist/*

echo "==> 6/7 Publication PyPI"
if ! confirm "Publier $PKG $VERSION sur PyPI ?" PUBLISH_PYPI; then
  echo "    Ignoré."
  echo "    Pour publier : PUBLISH_PYPI=1 bash $HERE/publish.sh"
elif [ ! -f "$HOME/.pypirc" ] && [ -z "${TWINE_PASSWORD:-}" ]; then
  echo "    !! Aucun identifiant disponible : ni ~/.pypirc ni TWINE_PASSWORD."
  echo "    !! Créez ~/.pypirc (voir la doc interne), puis relancez."
  exit 1
else
  "$VENV/bin/python" -m twine upload --non-interactive "$HERE"/dist/*
  echo "    Publié. Vérification dans 20 s…"
  sleep 20
  curl -s -o /dev/null -w "    pypi.org/project/$PKG -> HTTP %{http_code}\n" \
    "https://pypi.org/pypi/$PKG/json"
fi

echo "==> 7/7 Image Docker"
if ! command -v docker >/dev/null 2>&1; then
  echo "    docker introuvable — étape ignorée."
elif ! confirm "Construire et pousser $DOCKER_REPO:$VERSION ?" PUBLISH_DOCKER; then
  echo "    Ignoré.  (PUBLISH_DOCKER=1 pour l'activer)"
else
  docker build -t "$DOCKER_REPO:$VERSION" -t "$DOCKER_REPO:latest" "$HERE"
  docker run --rm "$DOCKER_REPO:$VERSION" --help >/dev/null && echo "    image fonctionnelle."
  docker push "$DOCKER_REPO:$VERSION"
  docker push "$DOCKER_REPO:latest"
fi

echo
echo "===================== RÉCAPITULATIF ====================="
echo " Paquet    : $PKG $VERSION"
echo " Artefacts : $(ls "$HERE"/dist 2>/dev/null | tr '\n' ' ')"
printf " PyPI      : HTTP %s  https://pypi.org/project/%s/\n" \
  "$(curl -s -o /dev/null -w '%{http_code}' -m 10 "https://pypi.org/pypi/$PKG/json")" "$PKG"
echo " Docker    : https://hub.docker.com/r/$DOCKER_REPO"
echo "========================================================="
