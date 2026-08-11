#!/bin/bash
# Double-cliquer ce fichier depuis le Finder.
# 1. Rapatrie les images depuis l'ancien WordPress vers static/img/
# 2. Reconstruit le site avec les images locales
# 3. Prépare docs/ et une archive prête pour la mise en ligne

cd "$(dirname "$0")" || exit 1

BOLD=$'\033[1m'; GREEN=$'\033[32m'; RED=$'\033[31m'; RESET=$'\033[0m'

echo "${BOLD}Orchestre de Chambre de Wissembourg — préparation du site${RESET}"
echo

command -v python3 >/dev/null || {
  echo "${RED}python3 introuvable.${RESET} Installe les outils Xcode : xcode-select --install"
  read -r -p "Appuie sur Entrée pour fermer."; exit 1
}

DEST="static/img"
mkdir -p "$DEST"

echo "${BOLD}[1/3] Téléchargement des médias${RESET}"
python3 - <<'PY' > /tmp/ocw-media.tsv
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
  if [ -s "$DEST/$name" ]; then
    echo "  = $name"
    ok=$((ok + 1))
    continue
  fi
  if curl -fsSL --retry 3 --max-time 120 -o "$DEST/$name" "$url"; then
    echo "  ${GREEN}+${RESET} $name"
    ok=$((ok + 1))
  else
    echo "  ${RED}! échec${RESET} $url"
    rm -f "$DEST/$name"
    ko=$((ko + 1))
  fi
done < /tmp/ocw-media.tsv
rm -f /tmp/ocw-media.tsv
echo "  → $ok fichier(s), $ko échec(s)"
echo

echo "${BOLD}[2/3] Redimensionnement des photos surdimensionnées${RESET}"
# sips est fourni par macOS : ramène les images à 1800 px de large maximum.
if command -v sips >/dev/null; then
  find "$DEST" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) -print0 |
    while IFS= read -r -d '' f; do
      w=$(sips -g pixelWidth "$f" 2>/dev/null | awk '/pixelWidth/{print $2}')
      if [ -n "$w" ] && [ "$w" -gt 1800 ]; then
        sips -Z 1800 "$f" >/dev/null 2>&1 && echo "  ↓ $(basename "$f") ($w → 1800 px)"
      fi
    done
else
  echo "  (sips indisponible, étape ignorée)"
fi
echo

echo "${BOLD}[3/3] Reconstruction du site${RESET}"
python3 build.py --local || { read -r -p "Erreur. Entrée pour fermer."; exit 1; }

rm -f site-ocw-docs.zip
( cd docs && zip -qr ../site-ocw-docs.zip . -x '.DS_Store' )
echo "  Archive : $(pwd)/site-ocw-docs.zip"
echo

echo "${GREEN}${BOLD}Terminé.${RESET}"
echo "Aperçu local  : python3 -m http.server -d docs 8000  →  http://localhost:8000"
echo "Mise en ligne : reviens dans Cowork, je prends la suite."
echo
open -R "$(pwd)/site-ocw-docs.zip" 2>/dev/null
read -r -p "Appuie sur Entrée pour fermer cette fenêtre."
