#!/usr/bin/env bash
# Rapatrie les médias depuis l'ancien WordPress vers static/img/,
# puis reconstruit le site en mode "images locales".
#
#   bash tools/download-images.sh
#
# À exécuter TANT QUE l'ancien site WordPress.com est encore en ligne :
# une fois l'abonnement résilié, les fichiers ne sont plus récupérables.

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="$ROOT/static/img"
mkdir -p "$DEST"

command -v python3 >/dev/null || { echo "python3 requis" >&2; exit 1; }

mapfile -t PAIRS < <(python3 - "$ROOT/content/media.json" <<'PY'
import json, sys
m = json.load(open(sys.argv[1], encoding="utf-8"))
base = m["wordpress_base"]
for f in m["files"].values():
    print(base + f["remote"] + "\t" + f["local"])
for name, path in m.get("documents", {}).items():
    print(base + path + "\t" + path.rsplit("/", 1)[-1])
PY
)

ok=0; ko=0
for pair in "${PAIRS[@]}"; do
  url="${pair%%$'\t'*}"; name="${pair##*$'\t'}"
  if [[ -s "$DEST/$name" ]]; then echo "= $name (déjà présent)"; ok=$((ok+1)); continue; fi
  if curl -fsSL --retry 2 --max-time 60 -o "$DEST/$name" "$url"; then
    echo "+ $name"; ok=$((ok+1))
  else
    echo "! ÉCHEC $url" >&2; rm -f "$DEST/$name"; ko=$((ko+1))
  fi
done

echo "---"
echo "$ok fichier(s) récupéré(s), $ko échec(s) → $DEST"

# Optimisation optionnelle : conversion WebP si cwebp est disponible.
if command -v cwebp >/dev/null; then
  echo "Génération des WebP…"
  find "$DEST" -type f \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) -print0 |
    while IFS= read -r -d '' f; do cwebp -quiet -q 82 "$f" -o "${f%.*}.webp"; done
fi

echo "Reconstruction en mode local :"
( cd "$ROOT" && python3 build.py --local )
