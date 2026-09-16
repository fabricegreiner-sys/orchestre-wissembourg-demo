#!/bin/bash
# Double-cliquer depuis le Finder.
# Prépare la vidéo de fond du bandeau d'accueil : découpe, redimensionne,
# supprime la piste audio, compresse en MP4 + WebM, puis reconstruit le site.
#
# Source idéale : une captation de concert de l'orchestre (10 à 15 secondes
# de plan large suffisent). À défaut, un plan d'archive libre de droits.

cd "$(dirname "$0")" || exit 1

BOLD=$'\033[1m'; GREEN=$'\033[32m'; RED=$'\033[31m'; YEL=$'\033[33m'; RESET=$'\033[0m'
DEST="static/video"
DUREE=12          # secondes conservées
LARGEUR_MAX=1920  # plafond ; on n'agrandit jamais au-delà de la source
CRF=26            # qualité H.264 : plus bas = plus net et plus lourd

fin() { echo; read -r -p "Appuie sur Entrée pour fermer."; exit "${1:-0}"; }

echo "${BOLD}Vidéo de fond du bandeau d'accueil${RESET}"
echo

if ! command -v ffmpeg >/dev/null; then
  echo "${RED}ffmpeg est requis.${RESET}"
  if command -v brew >/dev/null; then
    read -r -p "L'installer maintenant via Homebrew ? [O/n] " rep
    [[ "$rep" =~ ^[nN]$ ]] && fin 0
    brew install ffmpeg || fin 1
  else
    echo "Installe Homebrew puis : brew install ffmpeg"
    fin 1
  fi
fi

echo "Glisse le fichier vidéo source dans cette fenêtre, puis Entrée."
read -r -e SRC
SRC="${SRC%\'}"; SRC="${SRC#\'}"       # retire les quotes ajoutées par le Finder
SRC="${SRC/#\~/$HOME}"
[ -f "$SRC" ] || { echo "${RED}Fichier introuvable :${RESET} $SRC"; fin 1; }

echo
echo "À partir de quelle seconde découper ? (Entrée = 0)"
read -r DEBUT
DEBUT="${DEBUT:-0}"

mkdir -p "$DEST"

# Largeur réelle de la source : agrandir une vidéo n'ajoute aucun détail,
# ça ne fait que gonfler le fichier et accentuer le flou.
SRC_W=$(ffprobe -v error -select_streams v:0 -show_entries stream=width \
        -of csv=p=0 "$SRC" 2>/dev/null | tr -d '[:space:],')
if [ -n "$SRC_W" ] && [ "$SRC_W" -lt "$LARGEUR_MAX" ]; then
  LARGEUR="$SRC_W"
  echo "Source en ${SRC_W} px de large : on conserve cette résolution."
  [ "$SRC_W" -lt 1280 ] && echo "${YEL}Source peu définie — le rendu restera flou quel que soit l'encodage.${RESET}"
else
  LARGEUR="$LARGEUR_MAX"
  echo "Source en ${SRC_W:-?} px : réduction à ${LARGEUR} px."
fi

echo
echo "${BOLD}[1/3] Encodage MP4 (H.264)${RESET}"
ffmpeg -y -loglevel error -ss "$DEBUT" -i "$SRC" -t "$DUREE" \
  -an -vf "scale=${LARGEUR}:-2:flags=lanczos,fps=25" \
  -c:v libx264 -preset slow -crf "$CRF" -pix_fmt yuv420p -movflags +faststart \
  "$DEST/hero.mp4" || { echo "${RED}Échec de l'encodage MP4.${RESET}"; fin 1; }
echo "  $(du -h "$DEST/hero.mp4" | cut -f1)"

echo "${BOLD}[2/3] Encodage WebM (VP9) — plus léger sur Chrome et Firefox${RESET}"
ffmpeg -y -loglevel error -ss "$DEBUT" -i "$SRC" -t "$DUREE" \
  -an -vf "scale=${LARGEUR}:-2:flags=lanczos,fps=25" \
  -c:v libvpx-vp9 -crf 34 -b:v 0 -row-mt 1 \
  "$DEST/hero.webm" || echo "  ${YEL}WebM non généré, le MP4 suffira.${RESET}"
[ -f "$DEST/hero.webm" ] && echo "  $(du -h "$DEST/hero.webm" | cut -f1)"

# Garde-fou : un fond de plus de 3 Mo ruine le temps de chargement.
TAILLE=$(du -k "$DEST/hero.mp4" | cut -f1)
if [ "$TAILLE" -gt 5120 ]; then
  echo
  echo "${YEL}Attention : le MP4 pèse $((TAILLE / 1024)) Mo.${RESET}"
  echo "Au-delà de 5 Mo, la page devient lente sur mobile. Réduis DUREE, baisse"
  echo "LARGEUR_MAX, ou monte CRF (26 → 30) en haut de ce script."
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
echo "${GREEN}${BOLD}Vidéo installée.${RESET}"
echo "Aperçu : python3 -m http.server -d docs 8000  →  http://localhost:8000"
echo "Publication : 4-Mettre-a-jour-le-site.command"
fin 0
