# Orchestre de Chambre de Wissembourg — refonte statique

Clone modernisé du site `orchestre-wissembourg.com`, destiné à remplacer WordPress.com.
Trilingue FR/DE/PL, générateur maison en Python (stdlib uniquement), sortie 100 % statique.

## Pourquoi ce socle

| Critère | WordPress.com Premium | Ce site |
|---|---|---|
| Coût annuel | 96 € HT + domaine | **0 €** (Cloudflare) + domaine |
| Version allemande structurée | non | **oui** (`/fr/`, `/de/`, `hreflang`) |
| Cookies tiers au chargement | oui (stats, barre WP) | **aucun** — vidéos YouTube en façade cliquable |
| Poids / dépendances | thème + JS WordPress | 1 CSS, 1 JS (~3 ko), aucune police externe |
| Surface d'attaque | PHP + base + comptes | **fichiers statiques** — rien à patcher |
| En-têtes de sécurité | non configurables | **note A** sur securityheaders.com |
| Sauvegarde / réversibilité | export XML | dépôt Git complet |

## Arborescence

```
site-ocw/
├── build.py              générateur (aucune dépendance)
├── content/
│   ├── media.json        table des médias : URL WordPress ↔ nom de fichier local
│   ├── fr.json           tout le contenu français (langue de référence)
│   ├── de.json           tout le contenu allemand
│   └── pl.json           tout le contenu polonais — généré par tools/make-pl.py
├── static/
│   ├── css/style.css     feuille de style unique
│   ├── js/main.js        menu mobile + façade vidéo RGPD
│   └── img/              médias locaux (après download-images.sh)
├── tools/download-images.sh
└── docs/                 ← SORTIE générée, racine de publication GitHub Pages
```

## Construire

```bash
python3 build.py            # images servies depuis l'ancien WordPress (mode démo)
python3 build.py --local    # images servies depuis assets/img/
```

Prévisualisation locale :

```bash
python3 -m http.server -d docs 8000    # http://localhost:8000
```

Les chemins sont **relatifs** : le site fonctionne en `file://`, dans un sous-dossier
(`domaine.tld/sous-dossier/`) ou à la racine d'un domaine, sans reconfiguration.

## Modifier le contenu

Tout est dans `content/fr.json`, `content/de.json` et `content/pl.json`. Aucun HTML à écrire :
chaque page est une liste de blocs typés.

| Bloc | Usage |
|---|---|
| `hero` | bandeau d'accueil plein écran |
| `pagehead` | en-tête des pages intérieures |
| `prose` | texte libre (HTML autorisé dans `html`) |
| `split` | texte + image côte à côte (`image_right` pour inverser) |
| `stats` | chiffres clés |
| `posterFeatured` / `posters` | affiche à la une / galerie d'affiches |
| `events` | agenda structuré (date, lieu, programme) |
| `videos` | vidéos YouTube en façade cliquable |
| `cards`, `desks`, `clips` | cartes, pupitres, coupures de presse |
| `sponsors`, `seasons` | logos partenaires, archives de saisons |
| `contact`, `cta` | coordonnées + lien mailto, bandeau d'appel à l'action |
| `timeline`, `quote` | frise de parcours, citation mise en exergue |

Options communes : `eyebrow`, `h2`, `alt` (fond alterné), `ink` (fond sombre),
`narrow` (colonne étroite), `buttons`.

Liens : `page:agenda`, `page:soutenir#mecenat`, `media:logo`, ou une URL complète.

## Récupérer les images avant de couper WordPress

**À faire tant que l'abonnement WordPress.com est actif.** En mode démo, les images
sont encore servies par l'ancien site ; elles disparaîtront à la résiliation.

```bash
bash tools/download-images.sh
```

Le script télécharge tous les médias listés dans `content/media.json` vers
`static/img/`, génère les WebP si `cwebp` est installé, puis relance le build
en mode local.

## Héberger

**Dépôt sur GitHub, hébergement sur Cloudflare.** Le dépôt reste la source ;
Cloudflare sert `docs/` et applique `_headers`.

Le Worker est configuré par `wrangler.jsonc` : `assets.directory` pointe sur
`./docs`, et il n'y a **délibérément pas de clé `main`** — un Worker
« assets-only ». Ajouter un script désactiverait l'application automatique de
`_headers`.

Piège du tableau de bord : créer un *Worker* au lieu d'un projet *Pages* fait
disparaître le champ « Build output directory ». C'est normal, `wrangler.jsonc`
le remplace.

L'URL publique se déclare dans `.baseurl` à la racine. Le script de publication
la lit en priorité ; elle alimente les URL canoniques, les `hreflang` et le
sitemap. La changer d'hébergeur revient à éditer ce fichier et à reconstruire.

Mise à jour courante : double-clic sur `4-Mettre-a-jour-le-site.command`
(reconstruit, commite, pousse). `3-Corriger-et-republier.command` est réservé
aux réparations lourdes — il recrée le dépôt git et force le push.

## Basculer le domaine orchestre-wissembourg.com

Ordre à respecter — ne pas résilier WordPress avant que le nouveau site soit validé.

1. Récupérer les images (`tools/download-images.sh`), rebuild, commit, push.
2. Transférer le nom de domaine hors de WordPress.com : déverrouiller, récupérer
   le code d'autorisation, transférer chez le registrar retenu. **Titulaire = l'association**,
   pas le prestataire. Impossible dans les 60 jours suivant un enregistrement ou un
   transfert précédent.
3. Dans le Worker Cloudflare : Settings → Domains & Routes → Add custom domain,
   saisir `orchestre-wissembourg.com` puis `www.orchestre-wissembourg.com`.
   Si le domaine est dans le même compte Cloudflare, les enregistrements DNS et le
   certificat sont créés automatiquement ; sinon, suivre les valeurs indiquées.
4. Mettre `.baseurl` à `https://orchestre-wissembourg.com`, reconstruire, pousser —
   canonical, hreflang et sitemap suivent.
5. Vérifier les trois langues, le sitemap, les redirections et un scan
   securityheaders.com, puis seulement résilier l'abonnement WordPress.com.

Prévoir un TTL court (300 s) avant la bascule, et garder l'export WordPress
(Outils → Exporter) comme filet de sécurité.

## En-têtes de sécurité HTTP

`build.py` génère `docs/_headers` : HSTS, CSP stricte, `X-Frame-Options`,
`X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy` et les en-têtes
cross-origin. Cloudflare les applique — **note A sur securityheaders.com**.

À savoir si l'on envisage un autre hébergeur : **GitHub Pages ignore ce fichier**
et ne permet aucun en-tête personnalisé, quelle que soit la configuration. Un scan
y donnera toujours F. Ce n'est pas un défaut du site.

La CSP n'autorise **aucun script inline** : le JSON-LD est validé par empreinte
SHA-256 recalculée à chaque build, et le script de redirection de langue est
externalisé dans `assets/js/lang-redirect.js`. Aucun attribut `style=` en ligne
non plus, d'où les classes utilitaires `u-*` de la feuille de style. Chaque page
embarque en plus la CSP en balise `meta`, utile si le site est un jour servi par
un hébergeur sans en-têtes.

**Toute nouvelle ressource externe — police, carte, widget HelloAsso — doit être
déclarée dans la fonction `csp()` de `build.py`**, sinon le navigateur la bloquera
silencieusement. Après ajout, vérifier la console du navigateur.

## Reste à configurer

- **Adresse e-mail** : la page contact renvoie vers `contact@orchestre-wissembourg.com`,
  qui n'existe pas encore. À créer en redirection chez le registrar, vers la boîte
  du bureau. Sans elle, le seul lien de contact du site est mort.
- **Don / adhésion / billetterie** : les boutons pointent vers `helloasso.com` →
  à remplacer par les URLs des formulaires réels une fois le compte association créé.
- **Interface d'édition pour le bureau** : le dépôt contient le résultat généré,
  donc modifier `content/*.json` ne reconstruit rien. Il faut d'abord une GitHub
  Action qui exécute `build.py`, puis un CMS (Decap ou Sveltia). À développer
  seulement une fois le devis signé.
- **Contenus à obtenir de l'association** : programme réel de la saison en cours,
  liste nominative des musiciens par pupitre, noms et sites des sept sponsors,
  textes alternatifs des affiches, dates du parcours de Marc Bender pour la frise.
- **Bandeau « maquette de démonstration »** : défini par la clé `ribbon` dans
  les fichiers `content/*.json` — le vider avant la mise en production.
- **Désactiver GitHub Pages** dans les réglages du dépôt, pour ne pas laisser
  deux copies du site en ligne.


## La version polonaise

L'orchestre joue avec des musiciens polonais (concerts trinationaux dans
l'esprit du Triangle de Weimar). La troisième langue est donc du contenu,
pas un gadget.

`content/pl.json` n'est **pas** édité à la main : il est régénéré par

    python3 tools/make-pl.py

qui recopie la structure de `content/fr.json` à l'identique et remplace
chaque chaîne via la table `tools/pl-translations.json` (un simple
dictionnaire « chaîne française » → « chaîne polonaise », éditable sans
toucher au code). Toute chaîne absente de la table
est affichée en fin d'exécution — impossible de livrer une page à moitié
française sans le voir. Neuf chaînes restent volontairement non traduites :
noms propres, adresse e-mail, noms des membres du bureau.

Conséquence pratique : **une modification de contenu se fait dans `fr.json`**,
puis on ajoute la traduction dans `tools/pl-translations.json` et on
régénère. Éditer directement `pl.json` revient à voir ses changements écrasés
au prochain passage du script.

Une relecture par un locuteur natif reste souhaitable avant de montrer la
version polonaise au bureau.


## Don, adhésion, billetterie (HelloAsso)

Le compte de l'association existe :
<https://www.helloasso.com/associations/orchestre-de-chambre-de-wissembourg>

Tous les liens de paiement passent par **une seule clé** `helloasso` à la
racine de chaque fichier de contenu :

    "helloasso": {
      "base":        "https://www.helloasso.com/associations/orchestre-de-chambre-de-wissembourg",
      "don":         "",
      "adhesion":    "",
      "billetterie": "",
      "widget":      ""
    }

Dans les blocs, on écrit `"link": "ha:don"` et non l'URL. `resolve_href()`
résout `ha:<clé>` et **retombe sur `base` quand la clé est vide** : aucun lien
mort tant que le formulaire n'est pas publié, et une seule valeur à changer
le jour où il l'est.

Pour renseigner ces URL sans éditer les JSON : `7-Activer-le-don-HelloAsso.command`
(il refuse toute URL qui ne pointe pas sur le compte de l'association, écrit
dans les trois langues, reconstruit et affiche le résultat).

`widget` n'est à remplir que pour un formulaire **embarqué en iframe**. Le
renseigner ajoute automatiquement `https://www.helloasso.com` au `frame-src`
de la CSP — c'est la seule raison d'ouvrir ce domaine. Par défaut on ne
l'embarque pas : le lien sortant ne charge rien de tiers sur le site.
