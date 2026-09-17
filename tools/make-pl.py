# -*- coding: utf-8 -*-
"""Génère content/pl.json depuis content/fr.json.
La structure est copiée à l'identique ; seules les chaînes présentes dans T
sont remplacées. Toute chaîne non traduite est signalée en fin d'exécution :
impossible de livrer une page à moitié française sans s'en apercevoir."""
import json, copy, pathlib

SKIP_KEYS = {"type","image","src","id","icon","video","motion","crop",
             "alt","logo","poster","n","lang","locale","base_url","og_image","same_as",
             "youtube","file","class","tone","variant","doc","slug","style","ratio","fit","link","base","widget","start","place"}

TABLE = pathlib.Path(__file__).with_name("pl-translations.json")
T = json.loads(TABLE.read_text(encoding="utf-8"))

missing = []
def tr(o, path=""):
    if isinstance(o, dict):
        return {k: (v if k in SKIP_KEYS or k.startswith("_") else tr(v, f"{path}.{k}"))
                for k, v in o.items()}
    if isinstance(o, list):
        return [tr(v, f"{path}[{i}]") for i, v in enumerate(o)]
    if isinstance(o, str):
        if o in T:
            return T[o]
        if o.startswith("Saison 20"):          # « Saison 2013-2014 » → « Sezon 2013-2014 »
            return "Sezon " + o[7:]
        if o.startswith("mailto:") and "?subject=" in o:
            # L'objet pré-rempli est vu par l'utilisateur : il se traduit aussi.
            adr, sujet = o.split("?subject=", 1)
            if sujet in T:
                return f"{adr}?subject={T[sujet]}"
            missing.append((path + " [objet mailto]", sujet))
            return o
        if o.strip() and not o.startswith(("http", "page:", "media:", "ha:", "#", "mailto:")) and not o.isdigit():
            missing.append((path, o))
        return o
    return o

src = json.load(open("content/fr.json", encoding="utf-8"))
out = tr(copy.deepcopy(src))
out["lang"] = "pl"
out["locale"] = "pl_PL"
pathlib.Path("content/pl.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(f"pl.json écrit — {len(missing)} chaîne(s) non traduite(s)")
for p, s in missing:
    print(f"  {p} :: {s[:110]}")
