#!/bin/bash
# Double-cliquer depuis le Finder.
# Rapatrie la photo de groupe en haute définition depuis l'ancien WordPress
# (original 5472 px) et la prépare pour le travelling du bandeau d'accueil.
#
# Sans ce fichier, le bandeau utilise la photo redimensionnée à 1800 px :
# suffisante en plan large, un peu tendre dès que le travelling zoome.

cd "$(dirname "$0")" || exit 1

BOLD=$'\033[1m'; GREEN=$'\033[32m'; RED=$'\033[31m'; YEL=$'\033[33m'; RESET=$'\033[0m'
DEST="static/img"
FICHIER="orchestre-tutti-hd.jpg"
LARGEUR=3000      # compromis netteté / poids pour un fond animé
QUALITE=72

fin() { echo; read -r -p "Appuie sur Entrée pour fermer."; exit "${1:-0}"; }

echo "${BOLD}Photo d'accueil en haute définition${RESET}"
echo

URL=$(python3 - <<'PY'
import json
m = json.load(open("content/media.json", encoding="utf-8"))
print(m["wordpress_base"] + m["files"]["hero_hd"]["remote"])
PY
)
echo "Source : $URL"
mkdir -p "$DEST"

echo
echo "${BOLD}[1/3] Téléchargement de l'original${RESET}"
curl -fsSL --retry 3 --max-time 180 -o "$DEST/$FICHIER" "$URL" || {
  echo "${RED}Échec.${RESET} L'abonnement WordPress est-il toujours actif ?"
  fin 1; }
echo "  $(du -h "$DEST/$FICHIER" | cut -f1)"

echo "${BOLD}[2/3] Redimensionnement à ${LARGEUR} px${RESET}"
if command -v sips >/dev/null; then
  W=$(sips -g pixelWidth "$DEST/$FICHIER" | awk '/pixelWidth/{print $2}')
  echo "  original : ${W} px de large"
  if [ -n "$W" ] && [ "$W" -gt "$LARGEUR" ]; then
    sips -Z "$LARGEUR" -s format jpeg -s formatOptions "$QUALITE" \
         "$DEST/$FICHIER" --out "$DEST/$FICHIER" >/dev/null 2>&1
    echo "  réduit à ${LARGEUR} px — $(du -h "$DEST/$FICHIER" | cut -f1)"
  else
    echo "  ${YEL}déjà sous le seuil, aucun redimensionnement.${RESET}"
  fi
fi

TAILLE=$(du -k "$DEST/$FICHIER" | cut -f1)
if [ "$TAILLE" -gt 1024 ]; then
  echo "  ${YEL}Attention : $((TAILLE))  ko. Baisse QUALITE ou LARGEUR si le chargement traîne.${RESET}"
fi

echo
echo "${BOLD}[3/3] Reconstruction du site${RESET}"
BASE=$( [ -s .baseurl ] && tr -d '[:space:]' < .baseurl )
IMGFLAG=""
[ -n "$(ls -A static/img 2>/dev/null)" ] && IMGFLAG="--local"
if [ -n "$BASE" ]; then
  python3 build.py $IMGFLAG --base-url "$BASE" || fin 1
else
  python3 build.py $IMGFLAG || fin 1
fi

echo
echo "${GREEN}${BOLD}Terminé.${RESET} Le bandeau utilise désormais la version haute définition."
echo "Aperçu : python3 -m http.server -d docs 8000  →  http://localhost:8000"
echo "Publication : 4-Mettre-a-jour-le-site.command"
fin 0
