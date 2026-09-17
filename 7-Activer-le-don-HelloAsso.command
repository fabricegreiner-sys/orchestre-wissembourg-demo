#!/bin/bash
# Double-cliquer depuis le Finder.
# Branche les boutons « Donner en ligne », « Adhérer » et « Réserver » du site
# sur les vrais formulaires HelloAsso, une fois qu'ils ont été publiés par le
# bureau de l'association.
#
# Tant qu'une URL n'est pas renseignée, le bouton correspondant retombe sur la
# page publique de l'association : aucun lien mort, jamais.

cd "$(dirname "$0")" || exit 1

LOG="$(pwd)/publication.log"
exec > >(tee -a "$LOG") 2>&1

BOLD=$'\033[1m'; GREEN=$'\033[32m'; RED=$'\033[31m'; YEL=$'\033[33m'; RESET=$'\033[0m'
ASSO="https://www.helloasso.com/associations/orchestre-de-chambre-de-wissembourg"

fin() { echo; echo "Journal : $LOG"; read -r -p "Appuie sur Entrée pour fermer."; exit "${1:-0}"; }

echo; echo "${BOLD}Activation des liens HelloAsso — $(date)${RESET}"
echo
echo "Page de l'association : $ASSO"
echo
echo "Colle l'URL de chaque formulaire publié sur HelloAsso."
echo "Laisse vide et appuie sur Entrée pour ne pas toucher à une valeur."
echo "Tape ${BOLD}-${RESET} pour effacer une valeur déjà enregistrée."
echo

read -r -p "Formulaire de DON          : " DON
read -r -p "Formulaire d'ADHÉSION      : " ADH
read -r -p "BILLETTERIE                : " BIL

python3 - "$DON" "$ADH" "$BIL" <<'PY' || fin 1
import json, pathlib, sys

CLES = ("don", "adhesion", "billetterie")
ATTENDU = "https://www.helloasso.com/associations/orchestre-de-chambre-de-wissembourg"
saisies = dict(zip(CLES, sys.argv[1:4]))

# Une URL qui ne pointe pas sur le compte de l'association est presque
# toujours une erreur de copier-coller : on refuse plutôt que de publier
# un bouton qui enverrait les donateurs ailleurs.
for cle, val in saisies.items():
    v = val.strip()
    if v and v != "-" and not v.startswith(ATTENDU):
        sys.exit(f"\033[31mURL refusée pour « {cle} » :\033[0m {v}\n"
                 f"Elle doit commencer par {ATTENDU}")

change = []
for lang in ("fr", "de", "pl"):
    f = pathlib.Path(f"content/{lang}.json")
    d = json.loads(f.read_text(encoding="utf-8"))
    ha = d.setdefault("helloasso", {})
    for cle, val in saisies.items():
        v = val.strip()
        if not v:
            continue
        nouveau = "" if v == "-" else v
        if ha.get(cle) != nouveau:
            ha[cle] = nouveau
            if lang == "fr":
                change.append(f"  {cle:12s} → {nouveau or '(repli sur la page de l’association)'}")
    f.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if change:
    print("\nModifications :")
    print("\n".join(change))
else:
    print("\nAucun changement.")
PY

echo
echo "${YEL}Rappel : le polonais est régénéré depuis le français.${RESET}"
echo "Ce script écrit directement dans les trois fichiers, donc rien à refaire ici."

echo
echo "${BOLD}Reconstruction${RESET}"
BASE=$( [ -s .baseurl ] && tr -d '[:space:]' < .baseurl )
IMGFLAG=""
[ -n "$(ls -A static/img 2>/dev/null)" ] && IMGFLAG="--local"
if [ -n "$BASE" ]; then
  python3 build.py $IMGFLAG --base-url "$BASE" || fin 1
else
  python3 build.py $IMGFLAG || fin 1
fi

echo
echo "${BOLD}Vérification${RESET}"
grep -ho 'href="https://www.helloasso.com[^"]*"' docs/fr/*.html | sort -u | sed 's/^/  /'

echo
echo "${GREEN}${BOLD}Terminé.${RESET} Publier avec : 4-Mettre-a-jour-le-site.command"
fin 0
