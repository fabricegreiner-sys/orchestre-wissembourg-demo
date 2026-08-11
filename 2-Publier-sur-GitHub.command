#!/bin/bash
# Double-cliquer ce fichier APRÈS 1-Preparer-le-site.command
# Crée le dépôt GitHub, pousse le site et active GitHub Pages sur docs/.

cd "$(dirname "$0")" || exit 1

BOLD=$'\033[1m'; GREEN=$'\033[32m'; RED=$'\033[31m'; YEL=$'\033[33m'; RESET=$'\033[0m'
REPO="orchestre-wissembourg-demo"

fin() { echo; read -r -p "Appuie sur Entrée pour fermer cette fenêtre."; exit "${1:-0}"; }

echo "${BOLD}Publication sur GitHub Pages${RESET}"
echo

# --- Vérifications -----------------------------------------------------
if [ ! -d docs ] || [ -z "$(ls -A docs 2>/dev/null)" ]; then
  echo "${RED}Le dossier docs/ est vide.${RESET} Lance d'abord 1-Preparer-le-site.command"
  fin 1
fi

if [ ! -d static/img ] || [ -z "$(ls -A static/img 2>/dev/null)" ]; then
  echo "${YEL}Attention : aucune image locale dans static/img/.${RESET}"
  echo "Le site sera publié avec les images encore servies par WordPress."
  read -r -p "Continuer quand même ? [o/N] " rep
  [[ "$rep" =~ ^[oO]$ ]] || fin 0
fi

# --- GitHub CLI --------------------------------------------------------
if ! command -v gh >/dev/null; then
  echo "${BOLD}GitHub CLI (gh) n'est pas installé.${RESET}"
  if command -v brew >/dev/null; then
    read -r -p "L'installer maintenant via Homebrew ? [O/n] " rep
    [[ "$rep" =~ ^[nN]$ ]] && fin 0
    brew install gh || fin 1
  else
    echo "Installe Homebrew puis gh :"
    echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    echo "  brew install gh"
    fin 1
  fi
fi

echo "${BOLD}[1/4] Authentification GitHub${RESET}"
if ! gh auth status >/dev/null 2>&1; then
  echo "Une page GitHub va s'ouvrir dans ton navigateur pour autoriser l'accès."
  gh auth login -h github.com -p https -w || fin 1
fi
OWNER=$(gh api user --jq .login) || fin 1
echo "  Connecté en tant que ${GREEN}$OWNER${RESET}"
echo

# --- Dépôt local -------------------------------------------------------
echo "${BOLD}[2/4] Préparation du dépôt local${RESET}"
# Reconstruction avec l'URL publique réelle (canonical, hreflang, sitemap).
IMGFLAG=""
[ -n "$(ls -A static/img 2>/dev/null)" ] && IMGFLAG="--local"
python3 build.py $IMGFLAG --base-url "https://$OWNER.github.io/$REPO" || fin 1
[ -d .git ] || git init -q
git config user.name  >/dev/null 2>&1 || git config user.name  "$OWNER"
git config user.email >/dev/null 2>&1 || git config user.email "$OWNER@users.noreply.github.com"
git add -A
git commit -q -m "Refonte statique OCW — bilingue FR/DE, images locales" 2>/dev/null \
  && echo "  Commit créé." || echo "  Rien de nouveau à committer."
git branch -M main
echo

# --- Dépôt distant -----------------------------------------------------
echo "${BOLD}[3/4] Dépôt GitHub${RESET}"
if gh repo view "$OWNER/$REPO" >/dev/null 2>&1; then
  echo "  Le dépôt $OWNER/$REPO existe déjà, mise à jour."
  git remote get-url origin >/dev/null 2>&1 \
    || git remote add origin "https://github.com/$OWNER/$REPO.git"
  git push -u origin main || fin 1
else
  gh repo create "$OWNER/$REPO" --public --source=. --remote=origin --push \
    --description "Refonte statique bilingue du site de l'Orchestre de Chambre de Wissembourg" || fin 1
fi
echo

# --- Activation de Pages -----------------------------------------------
echo "${BOLD}[4/4] Activation de GitHub Pages${RESET}"
gh api -X POST "repos/$OWNER/$REPO/pages" \
  -f "source[branch]=main" -f "source[path]=/docs" >/dev/null 2>&1 \
  && echo "  Pages activé." \
  || { gh api -X PUT "repos/$OWNER/$REPO/pages" \
        -f "source[branch]=main" -f "source[path]=/docs" >/dev/null 2>&1 \
        && echo "  Pages déjà actif, configuration mise à jour." \
        || echo "  ${YEL}Activation automatique impossible.${RESET} Va dans Settings → Pages : branche main, dossier /docs."; }

URL="https://$OWNER.github.io/$REPO/"
echo
echo "${GREEN}${BOLD}Publié.${RESET}"
echo "  Dépôt : https://github.com/$OWNER/$REPO"
echo "  Site  : ${BOLD}$URL${RESET}"
echo "  (compter une à deux minutes pour le premier déploiement)"
echo
read -r -p "Ouvrir le site dans le navigateur ? [O/n] " rep
[[ "$rep" =~ ^[nN]$ ]] || { sleep 45; open "$URL"; }
fin 0
