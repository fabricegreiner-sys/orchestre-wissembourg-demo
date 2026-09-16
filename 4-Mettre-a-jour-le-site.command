#!/bin/bash
# Double-cliquer depuis le Finder.
# Reconstruit le site et publie la mise à jour sur GitHub Pages.
# Script de routine : contrairement au 3, il ne touche pas au dépôt git existant.

cd "$(dirname "$0")" || exit 1

LOG="$(pwd)/publication.log"
exec > >(tee -a "$LOG") 2>&1

BOLD=$'\033[1m'; GREEN=$'\033[32m'; RED=$'\033[31m'; YEL=$'\033[33m'; RESET=$'\033[0m'
REPO="orchestre-wissembourg-demo"

fin() { echo; echo "Journal : $LOG"; read -r -p "Appuie sur Entrée pour fermer."; exit "${1:-0}"; }

echo; echo "${BOLD}Mise à jour du site — $(date)${RESET}"

command -v python3 >/dev/null || { echo "${RED}python3 introuvable${RESET}"; fin 1; }
command -v gh      >/dev/null || { echo "${RED}gh introuvable — lance : brew install gh${RESET}"; fin 1; }
[ -d .git ] || { echo "${RED}Aucun dépôt git ici.${RESET} Lance d'abord 3-Corriger-et-republier.command"; fin 1; }

gh auth status >/dev/null 2>&1 || gh auth login -h github.com -p https -w || fin 1
OWNER=$(gh api user --jq .login) || fin 1

# URL publique réelle. Le fichier .baseurl prime : c'est lui qui porte l'adresse
# de l'hébergement de production (Cloudflare Workers), et il détermine les URL
# canoniques, les hreflang et le sitemap.
if [ -s .baseurl ]; then
  BASE=$(tr -d '[:space:]' < .baseurl)
else
  PAGES_HOST=$(gh api "repos/$OWNER/$OWNER.github.io/pages" --jq '.cname // empty' 2>/dev/null)
  [ -n "$PAGES_HOST" ] && BASE="https://$PAGES_HOST/$REPO" || BASE="https://$OWNER.github.io/$REPO"
fi

echo "${BOLD}[1/3] Reconstruction${RESET}"
IMGFLAG=""
[ -n "$(ls -A static/img 2>/dev/null)" ] && IMGFLAG="--local"
python3 build.py $IMGFLAG --base-url "$BASE" || { echo "${RED}Build en échec.${RESET}"; fin 1; }

echo "${BOLD}[2/3] Commit${RESET}"
git add -A || fin 1
if git diff --cached --quiet; then
  echo "  Aucune modification à publier."
  fin 0
fi
MSG="${1:-Mise à jour du site — $(date '+%d/%m/%Y %H:%M')}"
git commit -q -m "$MSG" || { echo "${RED}Commit en échec.${RESET}"; fin 1; }
echo "  $(git log -1 --pretty=%s)"

echo "${BOLD}[3/3] Envoi${RESET}"
BRANCH=$(git rev-parse --abbrev-ref HEAD)
git push origin "$BRANCH" || { echo "${RED}Push en échec.${RESET}"; fin 1; }

echo
echo "${GREEN}${BOLD}Publié.${RESET}  $BASE/"
echo "Compter une à deux minutes avant que la mise à jour soit visible."
read -r -p "Ouvrir le site ? [O/n] " rep
[[ "$rep" =~ ^[nN]$ ]] || { sleep 60; open "$BASE/fr/index.html"; }
fin 0
