#!/bin/bash
# Double-cliquer depuis le Finder.
# Répare la publication : dépôt git remis à neuf, images rapatriées en local,
# reconstruction avec la bonne URL, push forcé sur la branche master.
#
# Tout est journalisé dans publication.log — en cas d'échec, envoie-moi ce fichier.

cd "$(dirname "$0")" || exit 1

LOG="$(pwd)/publication.log"
exec > >(tee "$LOG") 2>&1

BOLD=$'\033[1m'; GREEN=$'\033[32m'; RED=$'\033[31m'; YEL=$'\033[33m'; RESET=$'\033[0m'
REPO="orchestre-wissembourg-demo"
BRANCH="master"          # doit correspondre à la source configurée dans Settings → Pages

fin() { echo; echo "Journal : $LOG"; read -r -p "Appuie sur Entrée pour fermer."; exit "${1:-0}"; }
etape() { echo; echo "${BOLD}$1${RESET}"; }

echo "${BOLD}Orchestre de Chambre de Wissembourg — correction et republication${RESET}"
echo "$(date)"

command -v python3 >/dev/null || { echo "${RED}python3 introuvable${RESET} — lance : xcode-select --install"; fin 1; }
command -v gh      >/dev/null || { echo "${RED}gh introuvable${RESET} — lance : brew install gh"; fin 1; }

gh auth status >/dev/null 2>&1 || gh auth login -h github.com -p https -w || fin 1
OWNER=$(gh api user --jq .login) || fin 1
echo "Compte GitHub : $OWNER"

# L'URL publique réelle dépend du domaine personnalisé du site utilisateur.
PAGES_HOST=$(gh api "repos/$OWNER/$OWNER.github.io/pages" --jq '.cname // empty' 2>/dev/null)
if [ -n "$PAGES_HOST" ]; then
  BASE="https://$PAGES_HOST/$REPO"
else
  BASE="https://$OWNER.github.io/$REPO"
fi
echo "URL publique  : $BASE/"

# --- 1. Images ---------------------------------------------------------
etape "[1/4] Rapatriement des médias"
DEST="static/img"
mkdir -p "$DEST"
python3 - > /tmp/ocw-media.tsv <<'PY'
import json
m = json.load(open("content/media.json", encoding="utf-8"))
base = m["wordpress_base"]
for f in m["files"].values():
    print(base + f["remote"] + "\t" + f["local"])
for path in m.get("documents", {}).values():
    print(base + path + "\t" + path.rsplit("/", 1)[-1])
PY

ok=0; ko=0
while IFS=$'\t' read -r url name; do
  [ -z "$url" ] && continue
  if [ -s "$DEST/$name" ]; then ok=$((ok+1)); continue; fi
  if curl -fsSL --retry 3 --max-time 120 -o "$DEST/$name" "$url"; then
    echo "  + $name"; ok=$((ok+1))
  else
    echo "  ${RED}! échec${RESET} $url"; rm -f "$DEST/$name"; ko=$((ko+1))
  fi
done < /tmp/ocw-media.tsv
rm -f /tmp/ocw-media.tsv
echo "  → $ok présent(s), $ko échec(s)"
[ "$ok" -eq 0 ] && { echo "${RED}Aucun média récupéré, on s'arrête.${RESET}"; fin 1; }

# Allègement : macOS fournit sips, aucune dépendance à installer.
if command -v sips >/dev/null; then
  find "$DEST" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) -print0 |
    while IFS= read -r -d '' f; do
      w=$(sips -g pixelWidth "$f" 2>/dev/null | awk '/pixelWidth/{print $2}')
      if [ -n "$w" ] && [ "$w" -gt 1800 ]; then
        sips -Z 1800 "$f" >/dev/null 2>&1 && echo "  ↓ $(basename "$f") ($w → 1800 px)"
      fi
    done
fi

# --- 2. Reconstruction -------------------------------------------------
etape "[2/4] Reconstruction du site (images locales)"
python3 build.py --local --base-url "$BASE" || { echo "${RED}Build en échec.${RESET}"; fin 1; }
if [ ! -d docs/assets/img ] || [ -z "$(ls -A docs/assets/img)" ]; then
  echo "${RED}docs/assets/img est vide après le build.${RESET}"; fin 1
fi
echo "  docs/assets/img : $(ls docs/assets/img | wc -l | tr -d ' ') fichier(s)"

# --- 3. Dépôt git remis à neuf -----------------------------------------
# Le dépôt initial contenait des verrous git non supprimables (créés hors macOS),
# ce qui faisait échouer silencieusement commit et renommage de branche.
etape "[3/4] Réinitialisation du dépôt git"
rm -rf .git || { echo "${RED}Impossible de supprimer .git${RESET}"; fin 1; }
git init -q -b "$BRANCH" || fin 1
git config user.name  "$OWNER"
git config user.email "$OWNER@users.noreply.github.com"
git add -A || fin 1
git commit -q -m "Refonte statique OCW — bilingue FR/DE, images locales, corrections visuelles" || {
  echo "${RED}Commit en échec.${RESET}"; fin 1; }
echo "  $(git rev-list --count HEAD) commit, $(git ls-files | wc -l | tr -d ' ') fichier(s) suivis"

# --- 4. Push -----------------------------------------------------------
etape "[4/4] Envoi vers GitHub"
gh repo view "$OWNER/$REPO" >/dev/null 2>&1 || \
  gh repo create "$OWNER/$REPO" --public \
    --description "Refonte statique bilingue du site de l'Orchestre de Chambre de Wissembourg" || fin 1
git remote add origin "https://github.com/$OWNER/$REPO.git"
git push -u --force origin "$BRANCH" || { echo "${RED}Push en échec.${RESET}"; fin 1; }

gh api -X PUT "repos/$OWNER/$REPO/pages" \
  -f "source[branch]=$BRANCH" -f "source[path]=/docs" >/dev/null 2>&1 \
  && echo "  Source Pages confirmée : $BRANCH /docs" \
  || echo "  ${YEL}Vérifie Settings → Pages : branche $BRANCH, dossier /docs${RESET}"

echo
echo "${GREEN}${BOLD}Publié.${RESET}  $BASE/"
echo "Le déploiement prend une à deux minutes."
read -r -p "Ouvrir le site ? [O/n] " rep
[[ "$rep" =~ ^[nN]$ ]] || { sleep 60; open "$BASE/"; }
fin 0
