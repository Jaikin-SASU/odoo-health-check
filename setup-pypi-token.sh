#!/usr/bin/env bash
# Enregistre le token PyPI dans ~/.pypirc, sans jamais l'afficher.
#
# Choisit automatiquement la méthode disponible :
#   • terminal interactif -> saisie masquée
#   • sinon (via `! bash …`) -> lecture du presse-papier macOS
#
# Le token n'est jamais affiché, ni passé en argument (donc absent de
# l'historique shell et de la table des processus).
set -euo pipefail

RC="$HOME/.pypirc"
TOKEN=""
SOURCE=""

echo "==> 1/5 Récupération du token"
if [ -t 0 ]; then
  echo "    Mode terminal interactif."
  echo "    Créez un token sur https://pypi.org/manage/account/token/"
  printf "    Collez-le (invisible à la saisie) : "
  read -r -s TOKEN
  echo
  SOURCE="saisie masquée"
elif command -v pbpaste >/dev/null 2>&1; then
  echo "    Pas de terminal interactif — lecture du presse-papier."
  TOKEN="$(pbpaste | tr -d '[:space:]')"
  SOURCE="presse-papier"
else
  echo "    !! Ni terminal interactif ni presse-papier disponible."
  exit 1
fi

echo "==> 2/5 Validation (le token n'est jamais affiché)"
if [ -z "$TOKEN" ]; then
  echo "    !! Aucun token récupéré via $SOURCE."
  [ "$SOURCE" = "presse-papier" ] && \
    echo "       Copiez le token depuis PyPI (bouton « Copy »), puis relancez."
  exit 1
fi
case "$TOKEN" in
  pypi-*) ;;
  *) echo "    !! Ce n'est pas un token PyPI (doit commencer par 'pypi-')."
     echo "       Source : $SOURCE. Rien n'a été écrit."
     exit 1;;
esac
if [ "${#TOKEN}" -lt 50 ]; then
  echo "    !! Token anormalement court (${#TOKEN} caractères). Abandon."
  exit 1
fi
echo "    OK — préfixe reconnu, ${#TOKEN} caractères, via $SOURCE."

echo "==> 3/5 Sauvegarde de l'existant"
if [ -f "$RC" ]; then
  cp -p "$RC" "$RC.bak.$(date +%Y%m%d%H%M%S)"
  echo "    ancien ~/.pypirc sauvegardé"
else
  echo "    aucun fichier existant"
fi

echo "==> 4/5 Écriture protégée"
OLD_UMASK="$(umask)"; umask 077
cat > "$RC" <<PYPIRC
[distutils]
index-servers = pypi

[pypi]
username = __token__
password = $TOKEN
PYPIRC
umask "$OLD_UMASK"
chmod 600 "$RC"
unset TOKEN

echo "==> 5/5 Vérification et nettoyage"
printf "    fichier : %s\n" "$RC"
printf "    droits  : %s (attendu 600)\n" "$(stat -f '%Lp' "$RC")"
printf "    contenu : %s ligne password, %s ligne username\n" \
  "$(grep -c '^password' "$RC")" "$(grep -c '^username' "$RC")"
if [ "$SOURCE" = "presse-papier" ]; then
  printf '' | pbcopy && echo "    presse-papier vidé"
fi

echo
echo "Terminé. Publication :"
echo "  PUBLISH_PYPI=1 bash $(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/publish.sh"
