# Orchestre de Chambre de Wissembourg — refonte statique

Clone modernisé du site `orchestre-wissembourg.com`, destiné à remplacer WordPress.com.
Bilingue FR/DE, générateur maison en Python (stdlib uniquement), sortie 100 % statique.

## Pourquoi ce socle

| Critère | WordPress.com Premium | Ce site |
|---|---|---|
| Coût annuel | 96 € HT + domaine | **0 €** (GitHub Pages) + domaine |
| Version allemande structurée | non | **oui** (`/fr/`, `/de/`, `hreflang`) |
| Cookies tiers au chargement | oui (stats, barre WP) | **aucun** — vidéos YouTube en façade cliquable |
| Poids / dépendances | thème + JS WordPress | 1 CSS, 1 JS (~3 ko), aucune police externe |
| Surface d'attaque | PHP + base + comptes | **fichiers statiques** — rien à patcher |
| Sauvegarde / réversibilité | export XML | dépôt Git complet |

## Arborescence

```
site-ocw/
├── build.py              générateur (aucune dépendance)
├── content/
│   ├── media.json        table des médias : URL WordPress ↔ nom de fichier local
│   ├── fr.json           tout le contenu français
│   └── de.json           tout le contenu allemand
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
(`user.github.io/ocw/`) ou à la racine d'un domaine, sans reconfiguration.

## Modifier le contenu

Tout est dans `content/fr.json` et `content/de.json`. Aucun HTML à écrire :
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
| `contact`, `cta` | coordonnées + formulaire, bandeau d'appel à l'action |

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

## Publier sur GitHub Pages

```bash
cd site-ocw
git init && git add -A && git commit -m "Refonte statique OCW — FR/DE"
git branch -M main
git remote add origin git@github.com:<compte>/orchestre-wissembourg.git
git push -u origin main
```

Puis dans **Settings → Pages** du dépôt : *Source* = `Deploy from a branch`,
*Branch* = `main`, *Folder* = `/docs`. L'URL `https://<compte>.github.io/orchestre-wissembourg/`
est active en une à deux minutes.

## Basculer le domaine orchestre-wissembourg.com

Ordre à respecter — ne pas résilier WordPress avant que le nouveau site soit validé.

1. Récupérer les images (`tools/download-images.sh`), rebuild, commit, push.
2. Créer le fichier `CNAME` à la racine du dépôt contenant `orchestre-wissembourg.com`.
   `build.py` le recopie automatiquement dans `docs/`.
3. Chez le registrar (le domaine est aujourd'hui géré par WordPress.com — vérifier
   s'il faut d'abord le transférer ou seulement déléguer les DNS), remplacer les
   enregistrements par :

   ```
   @      A       185.199.108.153
   @      A       185.199.109.153
   @      A       185.199.110.153
   @      A       185.199.111.153
   @      AAAA    2606:50c0:8000::153
   @      AAAA    2606:50c0:8001::153
   @      AAAA    2606:50c0:8002::153
   @      AAAA    2606:50c0:8003::153
   www    CNAME   <compte>.github.io.
   ```

4. **Settings → Pages → Custom domain** : saisir `orchestre-wissembourg.com`,
   attendre la validation DNS, puis cocher **Enforce HTTPS** (certificat
   Let's Encrypt automatique, quelques minutes).
5. Vérifier les deux langues, le sitemap et les redirections, puis seulement
   résilier l'abonnement WordPress.com.

Prévoir un TTL court (300 s) sur les enregistrements avant la bascule, et garder
l'export WordPress (Outils → Exporter) comme filet de sécurité.

## En-têtes de sécurité HTTP

`build.py` génère `docs/_headers` : HSTS, CSP stricte sans `unsafe-inline`,
`X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`,
`Permissions-Policy` et les en-têtes cross-origin.

**GitHub Pages ignore ce fichier** — la plateforme ne permet aucun en-tête HTTP
personnalisé, quelle que soit la configuration. Un scan securityheaders.com y
donnera toujours F. Ce n'est pas un défaut du site, c'est une limite de
l'hébergeur.

Deux façons d'obtenir la note A :

1. **Cloudflare Pages** (recommandé) — connecter le dépôt, dossier de publication
   `docs`, aucune commande de build. Le fichier `_headers` est appliqué
   automatiquement. Gratuit, et le `_headers` gère aussi le cache des assets.
2. **Cloudflare en frontal de GitHub Pages** — passer le DNS par Cloudflare et
   ajouter les en-têtes via une Transform Rule de réponse. Plus de pièces mobiles.

En attendant, chaque page embarque une CSP en balise `meta` : elle protège
réellement le visiteur, mais reste invisible pour les scanners, qui ne lisent
que les en-têtes HTTP. `frame-ancestors`, HSTS et `Permissions-Policy` sont
inopérants en balise meta — d'où la nécessité de la bascule.

La CSP n'autorise aucun script inline : le JSON-LD est validé par empreinte
SHA-256 recalculée à chaque build, et le script de redirection de langue est
externalisé dans `assets/js/lang-redirect.js`. Aucun attribut `style=` en ligne
non plus, d'où les classes utilitaires `u-*` de la feuille de style. **Toute
nouvelle ressource externe doit être déclarée dans la fonction `csp()` de
`build.py`**, sinon le navigateur la bloquera.

## Reste à configurer

- **Formulaire de contact** : `action` pointe sur un identifiant Formspree fictif
  dans `content/*.json` → à remplacer par un vrai endpoint, ou par un service
  auto-hébergé si l'on veut éviter tout tiers.
- **Don / adhésion / billetterie** : les boutons pointent vers `helloasso.com` →
  à remplacer par les URLs des formulaires réels une fois le compte association créé.
- **Newsletter** : lien générique Brevo → à remplacer par l'URL du formulaire d'inscription.
- **Contenus à obtenir de l'association** : programme réel de la saison en cours,
  liste nominative des musiciens par pupitre, noms et sites des sept sponsors,
  textes alternatifs des affiches, adresse e-mail de contact publique.
- **Bandeau « maquette de démonstration »** : défini par la clé `ribbon` dans
  `content/fr.json` et `content/de.json` — le vider avant la mise en production.
