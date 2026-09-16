#!/usr/bin/env python3
"""
Générateur statique — Orchestre de Chambre de Wissembourg.

Aucune dépendance externe (stdlib uniquement).
    python3 build.py              -> images servies depuis l'ancien WordPress (démo)
    python3 build.py --local      -> images servies depuis assets/img/ (après tools/download-images.sh)

Sortie : ./docs/  (racine de publication GitHub Pages)
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
OUT = ROOT / "docs"

LANGS = ("fr", "de")
DEFAULT_LANG = "fr"
BASE_URL_OVERRIDE = ""  # renseigné par --base-url : canonical / hreflang / sitemap

# --------------------------------------------------------------------------
# Médias
# --------------------------------------------------------------------------

with (CONTENT / "media.json").open(encoding="utf-8") as fh:
    MEDIA = json.load(fh)

WP_BASE = MEDIA["wordpress_base"]
IMAGE_MODE = "remote"


def media(key: str) -> str:
    """Résout une clé média en URL (distante) ou chemin relatif (local)."""
    entry = MEDIA["files"].get(key)
    if entry is None:
        raise KeyError(f"média inconnu : {key!r}")
    if IMAGE_MODE == "local":
        return "../assets/img/" + entry["local"]
    return WP_BASE + entry["remote"]


# --------------------------------------------------------------------------
# Helpers de rendu
# --------------------------------------------------------------------------

def e(text: str) -> str:
    return html.escape(text or "", quote=True)


def img(key: str, alt: str, *, cls: str = "", lazy: bool = True, sizes: str = "") -> str:
    attrs = [f'src="{e(media(key))}"', f'alt="{e(alt)}"']
    if cls:
        attrs.append(f'class="{e(cls)}"')
    if lazy:
        attrs.append('loading="lazy" decoding="async"')
    else:
        attrs.append('decoding="async" fetchpriority="high"')
    if sizes:
        attrs.append(f'sizes="{e(sizes)}"')
    return "<img " + " ".join(attrs) + ">"


def buttons(items: list[dict], lang: str) -> str:
    if not items:
        return ""
    out = []
    for b in items:
        style = b.get("style", "primary")
        href = resolve_href(b["href"], lang)
        ext = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
        out.append(f'<a class="btn btn--{e(style)}" href="{e(href)}"{ext}>{e(b["label"])}</a>')
    return '<div class="btn-row">' + "".join(out) + "</div>"


def resolve_href(href: str, lang: str) -> str:
    """`page:slug` -> <slug>.html (chemins relatifs : file://, sous-dossier ou domaine
    racine fonctionnent sans reconfiguration) ; `media:key` -> URL média."""
    if href.startswith("page:"):
        slug = href[5:]
        anchor = ""
        if "#" in slug:
            slug, anchor = slug.split("#", 1)
            anchor = "#" + anchor
        target = "index" if slug in ("", "index") else slug
        return f"{target}.html{anchor}"
    if href.startswith("media:"):
        return media(href[6:])
    return href


def eyebrow(block: dict) -> str:
    return f'<p class="eyebrow">{e(block["eyebrow"])}</p>' if block.get("eyebrow") else ""


def heading(block: dict) -> str:
    return f'<h2>{e(block["h2"])}</h2>' if block.get("h2") else ""


def section_open(block: dict) -> str:
    cls = ["section"]
    if block.get("alt"):
        cls.append("section--alt")
    if block.get("ink"):
        cls.append("section--ink")
    wrap = "wrap narrow" if block.get("narrow") else "wrap"
    return f'<section class="{" ".join(cls)}"><div class="{wrap}">'


SECTION_CLOSE = "</div></section>"


# --------------------------------------------------------------------------
# Blocs
# --------------------------------------------------------------------------

def b_hero(b: dict, lang: str, ctx: dict) -> str:
    badges = "".join(f'<span class="badge">{e(x)}</span>' for x in b.get("badges", []))
    return f"""
<section class="hero">
  <div class="hero__media">{img(b["image"], b.get("image_alt", ""), lazy=False)}</div>
  <div class="wrap"><div class="hero__inner">
    {f'<div class="hero__badges">{badges}</div>' if badges else ''}
    <h1>{e(b["h1"])}</h1>
    <p class="hero__tag">{e(b.get("tagline", ""))}</p>
    <p class="lead">{b.get("lead", "")}</p>
    {buttons(b.get("buttons", []), lang)}
  </div></div>
</section>"""


def b_pagehead(b: dict, lang: str, ctx: dict) -> str:
    return f"""
<section class="page-head"><div class="wrap">
  {eyebrow(b)}<h1>{e(b["h1"])}</h1>
  {f'<p>{b["lead"]}</p>' if b.get("lead") else ''}
</div></section>"""


def b_prose(b: dict, lang: str, ctx: dict) -> str:
    return (section_open(b) + eyebrow(b) + heading(b) + b.get("html", "")
            + buttons(b.get("buttons", []), lang) + SECTION_CLOSE)


def b_split(b: dict, lang: str, ctx: dict) -> str:
    cls = "portrait"
    if b.get("fit") == "contain":
        cls += " portrait--contain"
    if b.get("ratio") == "tall":
        cls += " portrait--tall"
    media_col = f'<div class="portrait-wrap">{img(b["image"], b.get("image_alt", ""), cls=cls)}</div>'
    text_col = f'<div>{eyebrow(b)}{heading(b)}{b.get("html", "")}{buttons(b.get("buttons", []), lang)}</div>'
    inner = (text_col + media_col) if b.get("image_right") else (media_col + text_col)
    return section_open(b) + f'<div class="split">{inner}</div>' + SECTION_CLOSE


def b_stats(b: dict, lang: str, ctx: dict) -> str:
    items = "".join(
        f'<div class="stat"><span class="stat__n">{e(s["n"])}</span>'
        f'<span class="stat__l">{e(s["l"])}</span></div>'
        for s in b["items"]
    )
    return section_open(b) + f'<div class="stats">{items}</div>' + SECTION_CLOSE


def b_poster_featured(b: dict, lang: str, ctx: dict) -> str:
    return (section_open(b) + '<div class="poster-featured">'
            + f'<figure class="poster">{img(b["image"], b.get("image_alt", ""))}</figure>'
            + f'<div>{eyebrow(b)}{heading(b)}{b.get("html", "")}{buttons(b.get("buttons", []), lang)}</div>'
            + "</div>" + SECTION_CLOSE)


def b_posters(b: dict, lang: str, ctx: dict) -> str:
    items = "".join(
        f'<figure class="poster">{img(p["image"], p.get("caption", ""))}'
        f'<figcaption>{e(p.get("caption", ""))}</figcaption></figure>'
        for p in b["items"]
    )
    return (section_open(b) + eyebrow(b) + heading(b) + b.get("html", "")
            + f'<div class="posters">{items}</div>' + SECTION_CLOSE)


def b_events(b: dict, lang: str, ctx: dict) -> str:
    rows = []
    for ev in b["items"]:
        btn = ""
        if ev.get("link"):
            btn = (f'<a class="btn btn--dark btn--sm" href="{e(resolve_href(ev["link"], lang))}">'
                   f'{e(ev.get("link_label", "→"))}</a>')
        rows.append(f"""
<article class="event">
  <div class="event__date">
    <span class="event__day">{e(ev["day"])}</span>
    <span class="event__month">{e(ev["month"])}</span>
    <span class="event__year">{e(ev["year"])}</span>
  </div>
  <div><h3>{e(ev["title"])}</h3><p class="event__meta">{e(ev.get("meta", ""))}</p></div>
  {btn}
</article>""")
    note = f'<div class="note u-mt-32">{b["note"]}</div>' if b.get("note") else ""
    return (section_open(b) + eyebrow(b) + heading(b) + b.get("html", "")
            + "".join(rows) + note + SECTION_CLOSE)


def b_videos(b: dict, lang: str, ctx: dict) -> str:
    items = "".join(f"""
<div class="video">
  <button class="video__facade" data-video="{e(v["id"])}" data-title="{e(v["label"])}"
          type="button" aria-label="{e(ctx["play_label"])} : {e(v["label"])}">
    <span class="video__play" aria-hidden="true">&#9654;</span>
    <span class="video__label">{e(v["label"])}</span>
    <span class="video__note">{e(ctx["video_note"])}</span>
  </button>
</div>""" for v in b["items"])
    return (section_open(b) + eyebrow(b) + heading(b) + b.get("html", "")
            + f'<div class="grid grid--2">{items}</div>' + SECTION_CLOSE)


def b_cards(b: dict, lang: str, ctx: dict) -> str:
    items = []
    for c in b["items"]:
        m = f'<div class="card__media">{img(c["image"], c.get("title", ""))}</div>' if c.get("image") else ""
        link = ""
        if c.get("link"):
            href = resolve_href(c["link"], lang)
            ext = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
            link = f'<a class="btn btn--ghost btn--sm" href="{e(href)}"{ext}>{e(c.get("link_label", "→"))}</a>'
        items.append(f'<article class="card">{m}<div class="card__body">'
                     f'<h3>{e(c["title"])}</h3><p>{c.get("text", "")}</p>{link}</div></article>')
    return (section_open(b) + eyebrow(b) + heading(b) + b.get("html", "")
            + f'<div class="grid grid--3">{"".join(items)}</div>' + SECTION_CLOSE)


def b_desks(b: dict, lang: str, ctx: dict) -> str:
    items = "".join(
        f'<figure class="desk">{img(d["image"], d["label"])}'
        f'<figcaption>{e(d["label"])}</figcaption></figure>'
        for d in b["items"]
    )
    return (section_open(b) + eyebrow(b) + heading(b) + b.get("html", "")
            + f'<div class="grid grid--4">{items}</div>' + SECTION_CLOSE)


def b_clips(b: dict, lang: str, ctx: dict) -> str:
    items = []
    for c in b["items"]:
        link = ""
        if c.get("link"):
            link = (f'<a class="btn btn--ghost btn--sm" target="_blank" rel="noopener" '
                    f'href="{e(resolve_href(c["link"], lang))}">{e(c.get("link_label", "PDF"))}</a>')
        items.append(f'<article class="clip">{img(c["image"], c.get("title", ""))}'
                     f'<div class="clip__body"><span class="clip__source">{e(c.get("source", ""))}</span>'
                     f'<h3>{e(c["title"])}</h3><p class="muted">{c.get("text", "")}</p>{link}</div></article>')
    return (section_open(b) + eyebrow(b) + heading(b) + b.get("html", "")
            + f'<div class="grid grid--2">{"".join(items)}</div>' + SECTION_CLOSE)


def b_sponsors(b: dict, lang: str, ctx: dict) -> str:
    items = []
    for s in b["items"]:
        inner = img(s["image"], s.get("name", ""))
        if s.get("url"):
            inner = f'<a href="{e(s["url"])}" target="_blank" rel="noopener">{inner}</a>'
        items.append(f'<div class="sponsor" title="{e(s.get("name", ""))}">{inner}</div>')
    return (section_open(b) + eyebrow(b) + heading(b) + b.get("html", "")
            + f'<div class="sponsors">{"".join(items)}</div>'
            + buttons(b.get("buttons", []), lang) + SECTION_CLOSE)


def b_seasons(b: dict, lang: str, ctx: dict) -> str:
    items = "".join(
        f'<li><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["label"])}</a></li>'
        for s in b["items"]
    )
    return (section_open(b) + eyebrow(b) + heading(b) + b.get("html", "")
            + f'<ul class="seasons">{items}</ul>' + SECTION_CLOSE)


def b_contact(b: dict, lang: str, ctx: dict) -> str:
    info = "".join(f'<li><strong>{e(i["label"])}</strong>{i["value"]}</li>' for i in b["info"])

    # Variante sans formulaire : lien mailto direct, aucun service tiers, aucune donnée traitée.
    if not b.get("form"):
        m = b["mailto"]
        subjects = "".join(
            f'<li><a href="mailto:{e(m["address"])}?subject={e(s["subject"])}">{e(s["label"])}</a></li>'
            for s in m.get("subjects", [])
        )
        return f"""
<section class="section"><div class="wrap"><div class="split">
  <div>{eyebrow(b)}{heading(b)}{b.get("html", "")}<ul class="infolist">{info}</ul></div>
  <div>
    <h3>{e(m["title"])}</h3>
    <p class="lead">{m.get("html", "")}</p>
    <p><a class="btn btn--primary" href="mailto:{e(m["address"])}">{e(m["address"])}</a></p>
    {f'<p class="muted">{e(m["hint"])}</p>' if m.get("hint") else ''}
    {f'<ul class="seasons u-mt-18">{subjects}</ul>' if subjects else ''}
  </div>
</div></div></section>"""

    f = b["form"]
    fields = "".join(
        f'<div class="field"><label for="{e(x["id"])}">{e(x["label"])}</label>'
        + (f'<textarea id="{e(x["id"])}" name="{e(x["name"])}" required></textarea>'
           if x.get("type") == "textarea"
           else f'<input id="{e(x["id"])}" name="{e(x["name"])}" type="{e(x.get("type", "text"))}" required>')
        + "</div>"
        for x in f["fields"]
    )
    return f"""
<section class="section"><div class="wrap"><div class="split">
  <div>{eyebrow(b)}{heading(b)}{b.get("html", "")}<ul class="infolist">{info}</ul></div>
  <div>
    <h3>{e(f["title"])}</h3>
    <form class="form" action="{e(f["action"])}" method="POST">
      {fields}
      <label class="consent"><input type="checkbox" required> <span>{f["consent"]}</span></label>
      <button class="btn btn--primary" type="submit">{e(f["submit"])}</button>
      <p class="muted">{f.get("note", "")}</p>
    </form>
  </div>
</div></div></section>"""


def b_timeline(b: dict, lang: str, ctx: dict) -> str:
    items = "".join(
        f'<li class="timeline__item">'
        f'<span class="timeline__when">{e(i["when"])}</span>'
        f'<h3 class="timeline__what">{e(i["what"])}</h3>'
        f'<p>{i.get("text", "")}</p></li>'
        for i in b["items"]
    )
    return (section_open(b) + eyebrow(b) + heading(b) + b.get("html", "")
            + f'<ul class="timeline">{items}</ul>'
            + buttons(b.get("buttons", []), lang) + SECTION_CLOSE)


def b_quote(b: dict, lang: str, ctx: dict) -> str:
    cite = f'<figcaption>{e(b["cite"])}</figcaption>' if b.get("cite") else ""
    return (section_open(b) + eyebrow(b)
            + f'<figure class="quote"><p>{b["text"]}</p>{cite}</figure>'
            + SECTION_CLOSE)


def b_cta(b: dict, lang: str, ctx: dict) -> str:
    return (f'<section class="section"><div class="wrap"><div class="cta-band">'
            f'{eyebrow(b)}<h2>{e(b["h2"])}</h2><p>{b.get("html", "")}</p>'
            f'{buttons(b.get("buttons", []), lang)}</div></div></section>')


BLOCKS = {
    "hero": b_hero, "pagehead": b_pagehead, "prose": b_prose, "split": b_split,
    "stats": b_stats, "posterFeatured": b_poster_featured, "posters": b_posters,
    "events": b_events, "videos": b_videos, "cards": b_cards, "desks": b_desks,
    "clips": b_clips, "sponsors": b_sponsors, "seasons": b_seasons,
    "contact": b_contact, "cta": b_cta, "timeline": b_timeline, "quote": b_quote,
}


# --------------------------------------------------------------------------
# Gabarit de page
# --------------------------------------------------------------------------

def render_nav(data: dict, lang: str, current: str) -> str:
    links = []
    for item in data["nav"]:
        aria = ' aria-current="page"' if item["slug"] == current else ""
        links.append(f'<a href="{e(resolve_href("page:" + item["slug"], lang))}"{aria}>{e(item["label"])}</a>')
    return "".join(links)


def render_lang_switch(lang: str, slug: str) -> str:
    out = []
    for code in LANGS:
        cur = ' aria-current="true"' if code == lang else ""
        out.append(f'<a hreflang="{code}" href="../{code}/{slug}.html"{cur}>{code.upper()}</a>')
    return '<div class="lang">' + "".join(out) + "</div>"


def render_footer(data: dict, lang: str) -> str:
    f = data["footer"]
    cols = []
    for col in f["columns"]:
        items = "".join(
            f'<li><a href="{e(resolve_href(l["href"], lang))}"'
            + (' target="_blank" rel="noopener"' if resolve_href(l["href"], lang).startswith("http") else "")
            + f'>{e(l["label"])}</a></li>'
            for l in col["links"]
        )
        cols.append(f'<div><h4>{e(col["title"])}</h4><ul>{items}</ul></div>')
    return f"""
<footer class="site-footer"><div class="wrap">
  <div class="footer-grid">
    <div>
      <h4>{e(data["site_name"])}</h4>
      <p>{f["address"]}</p>
      <p>{f["blurb"]}</p>
    </div>
    {"".join(cols)}
  </div>
  <div class="footer-bottom">
    <span>{f["legal"]}</span>
    <span>{f["credit"]}</span>
  </div>
</div></footer>"""


PAGE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
{alternates}
<meta property="og:type" content="website">
<meta property="og:locale" content="{locale}">
<meta property="og:site_name" content="{site_name}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0e1726">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<link rel="icon" href="{favicon}">
<link rel="stylesheet" href="../assets/css/style.css">
<script type="application/ld+json">{jsonld}</script>
</head>
<body>
{ribbon}
<a class="skip" href="#main">{skip}</a>
<header class="site-header"><div class="wrap site-header__inner">
  <a class="brand" href="index.html">
    <img src="{logo}" alt="" width="44" height="44">
    <span class="brand__text">
      <span class="brand__name">{brand_name}</span>
      <span class="brand__tag">{brand_tag}</span>
    </span>
  </a>
  <nav class="nav" id="nav" aria-label="{nav_label}">{nav}</nav>
  <div class="header-actions">
    {lang_switch}
    <a class="btn btn--primary btn--sm" href="{support_href}">{support_label}</a>
    <button class="burger" type="button" aria-label="{menu_label}" aria-expanded="false" aria-controls="nav"><span></span></button>
  </div>
</div></header>
<main id="main">
{body}
</main>
{footer}
<script src="../assets/js/main.js" defer></script>
</body>
</html>
"""


# --------------------------------------------------------------------------
# En-têtes de sécurité
# --------------------------------------------------------------------------

def sha256_csp(text: str) -> str:
    """Empreinte d'un script inline, au format attendu par la CSP."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return "'sha256-" + base64.b64encode(digest).decode("ascii") + "'"


def csp(hashes: list[str], *, with_frame_ancestors: bool) -> str:
    """Politique de sécurité du contenu.

    Aucun 'unsafe-inline' : toutes les règles sont dans la feuille de style,
    et les seuls scripts en ligne (JSON-LD) sont autorisés par empreinte.
    """
    img = "'self' data:"
    if IMAGE_MODE != "local":
        img += " https://orchestre-wissembourg.com"
    parts = [
        "default-src 'self'",
        "base-uri 'self'",
        "object-src 'none'",
        "form-action 'self'",
        f"img-src {img}",
        "style-src 'self'",
        "script-src 'self' " + " ".join(hashes),
        "frame-src https://www.youtube-nocookie.com",
        "connect-src 'self'",
        "upgrade-insecure-requests",
    ]
    if with_frame_ancestors:
        # Ignoré lorsqu'il est délivré par balise meta : réservé au vrai en-tête HTTP.
        parts.insert(3, "frame-ancestors 'none'")
    return "; ".join(parts)


HEADERS_TEMPLATE = """\
# En-têtes de sécurité HTTP.
# Appliqué par Cloudflare (Pages ET Workers avec static assets) et par Netlify.
# GitHub Pages IGNORE ce fichier : la plateforme ne permet aucun en-tête personnalisé.
/*
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
  Content-Security-Policy: {csp}
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()
  Cross-Origin-Opener-Policy: same-origin
  Cross-Origin-Resource-Policy: same-origin
  X-Permitted-Cross-Domain-Policies: none

/assets/*
  Cache-Control: public, max-age=31536000, immutable
"""


def jsonld(data: dict, lang: str) -> str:
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "MusicGroup",
        "name": data["site_name"],
        "alternateName": "OCW",
        "url": data["base_url"] + f"/{lang}/",
        "logo": media("logo"),
        "foundingDate": "2013-12",
        "genre": ["Classical music", "Chamber music"],
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "8 Rue de l'ordre Teutonique",
            "postalCode": "67160",
            "addressLocality": "Wissembourg",
            "addressCountry": "FR",
        },
        "sameAs": data["same_as"],
    }, ensure_ascii=False)


def render_page(data: dict, slug: str, page: dict, lang: str) -> str:
    ctx = {"play_label": data["ui"]["play"], "video_note": data["ui"]["video_note"]}
    body = "\n".join(BLOCKS[b["type"]](b, lang, ctx) for b in page["blocks"])
    ld = jsonld(data, lang)
    alternates = "\n".join(
        f'<link rel="alternate" hreflang="{c}" href="{data["base_url"]}/{c}/{slug}.html">' for c in LANGS
    ) + f'\n<link rel="alternate" hreflang="x-default" href="{data["base_url"]}/{DEFAULT_LANG}/{slug}.html">'

    return PAGE.format(
        lang=lang,
        locale=data["locale"],
        title=e(page["title"]),
        description=e(page["description"]),
        canonical=f'{data["base_url"]}/{lang}/{slug}.html',
        alternates=alternates,
        site_name=e(data["site_name"]),
        og_image=e(media(page.get("og_image", "hero"))),
        favicon=e(media("logo")),
        logo=e(media("logo")),
        jsonld=ld,
        csp=e(csp([sha256_csp(ld)], with_frame_ancestors=False)),
        ribbon=data.get("ribbon", ""),
        skip=e(data["ui"]["skip"]),
        brand_name=e(data["brand_name"]),
        brand_tag=e(data["brand_tag"]),
        nav_label=e(data["ui"]["nav_label"]),
        menu_label=e(data["ui"]["menu"]),
        nav=render_nav(data, lang, slug),
        lang_switch=render_lang_switch(lang, slug),
        support_href=e(resolve_href(data["ui"]["support_href"], lang)),
        support_label=e(data["ui"]["support"]),
        body=body,
        footer=render_footer(data, lang),
    )


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------

def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    shutil.copytree(STATIC / "css", OUT / "assets" / "css", dirs_exist_ok=True)
    shutil.copytree(STATIC / "js", OUT / "assets" / "js", dirs_exist_ok=True)
    if (STATIC / "img").exists():
        shutil.copytree(STATIC / "img", OUT / "assets" / "img", dirs_exist_ok=True)

    count = 0
    slugs: list[str] = []
    base_url = ""
    ld_hashes: list[str] = []
    for lang in LANGS:
        with (CONTENT / f"{lang}.json").open(encoding="utf-8") as fh:
            data = json.load(fh)
        if BASE_URL_OVERRIDE:
            data["base_url"] = BASE_URL_OVERRIDE.rstrip("/")
        base_url = data["base_url"]
        ld_hashes.append(sha256_csp(jsonld(data, lang)))
        target = OUT / lang
        target.mkdir(parents=True, exist_ok=True)
        for slug, page in data["pages"].items():
            (target / f"{slug}.html").write_text(render_page(data, slug, page, lang), encoding="utf-8")
            count += 1
            if lang == DEFAULT_LANG:
                slugs.append(slug)

    # Redirection racine : détection de langue navigateur, repli FR.
    # Redirection racine. Le script est externalisé : aucun script inline,
    # la CSP peut donc rester stricte.
    (OUT / "assets" / "js" / "lang-redirect.js").write_text(
        '(function(){var l="%s";try{l=localStorage.getItem("ocw-lang")||'
        '((navigator.language||"fr").slice(0,2)==="de"?"de":"fr");}catch(e){}'
        'location.replace(l+"/index.html");})();\n' % DEFAULT_LANG,
        encoding="utf-8")

    (OUT / "index.html").write_text(f"""<!DOCTYPE html>
<html lang="{DEFAULT_LANG}"><head><meta charset="utf-8">
<title>Orchestre de Chambre de Wissembourg</title>
<link rel="canonical" href="{DEFAULT_LANG}/index.html">
<meta http-equiv="refresh" content="0; url={DEFAULT_LANG}/index.html">
<meta name="referrer" content="strict-origin-when-cross-origin">
<script src="assets/js/lang-redirect.js" defer></script>
</head><body><p><a href="{DEFAULT_LANG}/index.html">Orchestre de Chambre de Wissembourg</a></p></body></html>
""", encoding="utf-8")

    (OUT / "_headers").write_text(
        HEADERS_TEMPLATE.format(csp=csp(ld_hashes, with_frame_ancestors=True)),
        encoding="utf-8")

    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n", encoding="utf-8")

    urls = "".join(
        f"<url><loc>{base_url}/{lang}/{s}.html</loc>"
        f"<changefreq>monthly</changefreq></url>"
        for s in slugs for lang in LANGS
    )
    (OUT / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n', encoding="utf-8")

    cname = ROOT / "CNAME"
    if cname.exists():
        shutil.copy(cname, OUT / "CNAME")

    print(f"OK — {count} pages générées dans {OUT} (images : {IMAGE_MODE})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", action="store_true", help="servir les images depuis assets/img/")
    ap.add_argument("--base-url", default="", help="URL publique (canonical, hreflang, sitemap)")
    args = ap.parse_args()
    IMAGE_MODE = "local" if args.local else "remote"
    BASE_URL_OVERRIDE = args.base_url
    try:
        build()
    except KeyError as exc:
        sys.exit(f"Erreur de contenu : {exc}")
