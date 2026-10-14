#!/usr/bin/env python3
"""
Builds Samuel T Sawian's portfolio as plain static files.

    python3 _src/build.py

Only Python 3 is needed (no packages). Run it from anywhere; files are written
to the repository root, next to this _src folder.

>>> Set SITE_URL once the site has an address. <<<
GitHub Pages project site:  https://<username>.github.io/<repo>
Custom domain later:        https://www.example.com
Leave it empty and the build still works, but canonical links, social-share
image URLs, structured-data URLs and sitemap.xml are left out, because they
must be absolute addresses.
"""
import json, os, html, datetime, shutil

SITE_URL = "https://degrimboy.github.io/portfolio"   # e.g. "https://samuelsawian.github.io/portfolio"  (no trailing slash)

SITE_NAME = "Samuel T Sawian"
LINKEDIN = "https://www.linkedin.com/in/samuelsawian"
BLOG = "https://samuelsawian.substack.com/"
EMAIL = "ssawian@gmail.com"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("OUT") or ROOT   # where the built site is written
SRC = os.path.join(ROOT, "_src")
SIZES = json.load(open(os.path.join(SRC, "image-sizes.json")))
TODAY = datetime.date.today().isoformat()
YEAR = datetime.date.today().year
SITE_URL = SITE_URL.rstrip("/")

def esc(s): return html.escape(s, quote=True)

# ------------------------------------------------------------------ helpers
class Page:
    def __init__(self, path, title, desc, og, body, *, crumbs=None, jsonld=None,
                 og_type="website", nav=None, noindex=False, og_alt=None):
        self.path, self.title, self.desc, self.og, self.body = path, title, desc, og, body
        self.crumbs, self.jsonld, self.og_type, self.nav = crumbs or [], jsonld or [], og_type, nav
        self.noindex, self.og_alt = noindex, og_alt or title
    @property
    def depth(self): return 0 if self.path in ("", "404.html") else self.path.strip("/").count("/") + 1
    @property
    def root(self): return "../" * self.depth
    @property
    def out(self): return "404.html" if self.path == "404.html" else os.path.join(self.path, "index.html")
    def abs(self, p=None):
        p = self.path if p is None else p
        return f"{SITE_URL}/{p}" if SITE_URL else None

def img(page, name, alt, cls="", lazy=True, sizes="(max-width: 900px) 100vw, 60vw", style="", hi=False):
    w, h = SIZES[f"{name}.webp"]
    r = page.root + "assets/img/"
    srcset = ""
    if f"{name}-800.webp" in SIZES:
        srcset = f' srcset="{r}{name}-800.webp 800w, {r}{name}.webp {w}w" sizes="{sizes}"'
    a = [f'src="{r}{name}.webp"{srcset}', f'alt="{esc(alt)}"', f'width="{w}"', f'height="{h}"']
    if cls: a.append(f'class="{cls}"')
    if style: a.append(f'style="{style}"')
    a.append('fetchpriority="high"' if hi else ('loading="lazy" decoding="async"' if lazy else 'decoding="async"'))
    return "<img " + " ".join(a) + ">"

PREVIEW = os.environ.get("PREVIEW") == "1"   # links point at .../index.html (for hosts without folder URLs)

def L(page, target):            # link to another page, relative so it works on GitHub Pages sub-paths
    if PREVIEW: return page.root + target + "index.html" if (not target or target.endswith("/")) else page.root + target
    return page.root + target if target else (page.root or "./")

def play(links):
    if not links: return ""
    a = "".join(f'<a href="{u}" target="_blank" rel="noopener">{t}<span class="visually-hidden"> (opens in a new tab)</span><span aria-hidden="true">↗</span></a>' for t, u in links)
    return f'<div class="play" aria-label="Where to play">{a}</div>'

def video(vid, title, meta):
    # Thumbnail first; the YouTube player loads only when clicked (keeps pages fast). Without JS it opens YouTube.
    return f'''<figure class="video">
          <a class="yt" href="https://www.youtube.com/watch?v={vid}" data-yt="{vid}" data-title="{esc(title)}" target="_blank" rel="noopener">
            <img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="" width="480" height="360" loading="lazy" decoding="async">
            <span class="yt-play" aria-hidden="true"></span><span class="visually-hidden">Play video: {esc(title)}</span>
          </a>
          <figcaption><b>{esc(title)}</b><span class="meta">{meta}</span></figcaption>
        </figure>'''

def facts(rows):
    return '<dl class="facts">' + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in rows) + "</dl>"

def bullets(items):
    return '<ul class="highlights">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"

def crumbs_html(page):
    if not page.crumbs: return ""
    items = []
    for i, (name, target) in enumerate(page.crumbs):
        if i == len(page.crumbs) - 1:
            items.append(f'<li aria-current="page">{esc(name)}</li>')
        else:
            items.append(f'<li><a href="{L(page, target)}">{esc(name)}</a></li>')
    return f'<nav class="crumbs wrap" aria-label="Breadcrumb"><ol>{"".join(items)}</ol></nav>'

def crumbs_ld(page):
    if not page.crumbs or not SITE_URL: return None
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": page.abs(t)} for i, (n, t) in enumerate(page.crumbs)]}

PERSON = {
    "@type": "Person",
    "name": "Samuel T Sawian",
    "alternateName": "Samuel Sawian",
    "jobTitle": "Game Producer and Product Manager",
    "description": "Game producer, product manager and LiveOps lead running live, free-to-play games and digital products, building games since 2010.",
    "email": "mailto:ssawian@gmail.com",
    "sameAs": [LINKEDIN, BLOG],
    "address": {"@type": "PostalAddress", "addressLocality": "Shillong", "addressRegion": "Meghalaya", "addressCountry": "IN"},
    "worksFor": [{"@type": "Organization", "name": "Barking Deer Entertainment"}, {"@type": "Organization", "name": "Dentira"}],
    "alumniOf": [{"@type": "CollegeOrUniversity", "name": "Vancouver Film School"},
                 {"@type": "CollegeOrUniversity", "name": "National Institute of Design"},
                 {"@type": "CollegeOrUniversity", "name": "Bangalore University"}],
    "knowsLanguage": ["kha", "en", "hi"],
    "knowsAbout": ["Game design", "Game production", "LiveOps", "Product management", "Free-to-play games", "UX design", "Brand identity"],
}
def person():
    p = dict(PERSON)
    if SITE_URL:
        p["@id"] = f"{SITE_URL}/#person"; p["url"] = f"{SITE_URL}/"; p["image"] = f"{SITE_URL}/assets/img/portrait.webp"
    return p

NAV = [("Games", "games/"), ("Product", "product/"), ("About", "about/")]

def head(page):
    canon = page.abs()
    og_img = f"{SITE_URL}/assets/og/{page.og}.jpg" if SITE_URL else f"{page.root}assets/og/{page.og}.jpg"
    r = page.root
    lines = [
        "<!doctype html>", '<html lang="en-IN">', "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        f'<base href="{SITE_URL}/">' if page.noindex and SITE_URL else "",
        f"<title>{esc(page.title)}</title>",
        f'<meta name="description" content="{esc(page.desc)}">',
        f'<meta name="author" content="{SITE_NAME}">',
        '<meta name="robots" content="noindex">' if page.noindex else '<meta name="robots" content="index, follow, max-image-preview:large">',
        f'<link rel="canonical" href="{canon}">' if canon and not page.noindex else "",
        '<meta name="theme-color" content="#131615">',
        '<meta name="color-scheme" content="dark">',
        f'<link rel="icon" href="{r}favicon.ico" sizes="32x32">',
        f'<link rel="icon" href="{r}assets/favicon.svg" type="image/svg+xml">',
        f'<link rel="apple-touch-icon" href="{r}assets/apple-touch-icon.png">',
        f'<link rel="manifest" href="{r}site.webmanifest">',
        f'<link rel="preload" href="{r}assets/fonts/bricolage-grotesque-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>',
        f'<link rel="preload" href="{r}assets/fonts/instrument-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>',
        f'<link rel="stylesheet" href="{r}assets/site.css">',
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        f'<meta property="og:type" content="{page.og_type}">',
        f'<meta property="og:title" content="{esc(page.title)}">',
        f'<meta property="og:description" content="{esc(page.desc)}">',
        f'<meta property="og:url" content="{canon}">' if canon else "",
        f'<meta property="og:image" content="{og_img}">',
        '<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{esc(page.og_alt)}">',
        '<meta property="og:locale" content="en_IN">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{esc(page.title)}">',
        f'<meta name="twitter:description" content="{esc(page.desc)}">',
        f'<meta name="twitter:image" content="{og_img}">',
    ]
    graph = [x for x in page.jsonld + [crumbs_ld(page)] if x]
    if graph:
        lines.append('<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + "</script>")
    lines.append(f'<script src="{r}assets/site.js" defer></script>')
    lines.append("</head>")
    return "\n".join(l for l in lines if l)

def header(page):
    cur = ' aria-current="page"'
    links = "".join(
        f'<a href="{L(page, t)}"{cur if page.nav == t else ""}>{n}</a>' for n, t in NAV)
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <div class="wrap">
    <a class="mark" href="{L(page, "")}" aria-label="Samuel T Sawian, home">S<span>.</span>T<span>.</span>S</a>
    <nav class="nav" aria-label="Main">{links}</nav>
  </div>
</header>'''

def footer(page):
    links = "".join(f'<li><a href="{L(page, t)}">{n}</a></li>' for n, t in NAV)
    return f'''<footer class="end">
  <canvas id="waves2" aria-hidden="true"></canvas>
  <div class="wrap foot">
    <div class="foot-top">
      <p>Samuel T Sawian<span style="color:var(--accent)">.</span></p>
      <ul class="foot-links">{links}<li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li><a href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn</a></li><li><a href="{BLOG}" target="_blank" rel="noopener">Blog</a></li></ul>
    </div>
    <div class="row"><span>Shillong, India</span><span>© {YEAR} Samuel T Sawian</span></div>
  </div>
</footer>
<dialog class="lb" id="lb" aria-label="Image viewer">
  <button type="button" id="lbClose">Close</button>
  <img id="lbImg" alt="">
  <p id="lbCap"></p>
</dialog>'''

def render(page):
    return f'''{head(page)}
<body>
{header(page)}
<main id="main">
{crumbs_html(page)}
{page.body(page)}
</main>
{footer(page)}
</body>
</html>
'''

# ------------------------------------------------------------------ content
GAMES = [  # order also drives the previous / next links
    ("bingo-bash", "Bingo Bash"), ("farmville-2", "FarmVille 2"), ("teen-patti-gold", "Teen Patti Gold"),
    ("dr-nero", "The Curious Case of Dr Nero"), ("gameloft", "Gameloft"),
    ("stellar-forever", "Stellar Forever"),
]
PRODUCTS = [("recycled-earth", "Recycled Earth"), ("meghalayan-age", "Meghalayan Age")]

PLAY = {
    "bingo-bash": [("Google Play", "https://play.google.com/store/apps/details?id=air.com.bitrhymes.bingo"),
                   ("App Store", "https://apps.apple.com/us/app/bingo-bash-live-bingo-games/id509098112")],
    "farmville-2": [("Zynga", "https://www.zynga.com/games/farmville-2/"), ("Facebook", "https://apps.facebook.com/farmville-two/")],
    "teen-patti-gold": [("Google Play", "https://play.google.com/store/apps/details?id=com.teenpatti.hd.gold"),
                        ("App Store", "https://apps.apple.com/us/app/teen-patti-gold-poker-rummy/id889200846")],
}

def next_links(page, items, section):
    keys = [k for k, _ in items]
    me = page.path.strip("/").split("/")[-1]
    i = keys.index(me)
    index_name = {"games": "All games", "product": "All product work"}[section]
    prev_href, prev_n = (f"{section}/{items[i-1][0]}/", items[i-1][1]) if i > 0 else (f"{section}/", index_name)
    next_href, next_n = (f"{section}/{items[i+1][0]}/", items[i+1][1]) if i < len(items) - 1 else (f"{section}/", index_name)
    return f'''<nav class="next wrap" aria-label="More projects">
  <a href="{L(page, prev_href)}"><span class="label">Previous</span><b>{prev_n}</b></a>
  <a href="{L(page, next_href)}"><span class="label">Next</span><b>{next_n}</b></a>
</nav>'''

# ---------- home
def home_body(p):
    cards = [
        ("games/bingo-bash/", "bingo", "Bingo Bash key art", "GSN Games · Social casino", "Bingo Bash", "The world's #1 free-to-play bingo game, acquired by GSN for $165M.", ""),
        ("games/farmville-2/", "farmville", "FarmVille 2 farm scene", "Zynga · Simulation", "FarmVille 2", "Led the content team for a game that peaked at 40M monthly players.", "b2"),
        ("games/teen-patti-gold/", "teenpatti", "Teen Patti Gold card table", "Moonfrog Labs · Card game", "Teen Patti Gold", "A top-grossing three-card game with more than 4M monthly players.", "b3"),
        ("games/dr-nero/", "nero-1", "Dr Nero isometric jungle", "Serious game · RPG", "The Curious Case of Dr Nero", "An RPG that teaches research scientists to collaborate.", "b2"),
        ("product/recycled-earth/", "re-challenge", "Women sorting plastic waste", "UX · Branding · Android", "Recycled Earth", "Waste collection that put Mumbai's ragpickers back to work. Featured by UNICEF.", ""),
        ("product/meghalayan-age/", "ma-box", "Lakadong turmeric premium packaging", "Brand · Packaging", "Meghalayan Age", "Brand and packaging for Meghalaya's finest produce.", "b3"),
    ]
    grid = "".join(f'''<a class="work-card" href="{L(p, href)}">
        <div class="blob {b}">{img(p, im, alt, sizes="(max-width: 560px) 100vw, (max-width: 900px) 50vw, 33vw")}</div>
        <span class="meta">{meta}</span><h3>{t}</h3><p>{d}</p></a>''' for href, im, alt, meta, t, d, b in cards)
    return f'''<section class="hero" aria-labelledby="intro-title">
    <canvas id="waves" aria-hidden="true"></canvas>
    <div class="wrap">
      <div>
        <h1 id="intro-title">Samuel T<br>Sawian<em>.</em></h1>
        <p class="label tagline">Creative director · Storyteller · Forest seeker</p>
        <p class="lede">I've been making games that people come back to every day since 2010. <span>Every feature I build starts with a small story: a farm that has never had a rooster, a scientist searching an alien planet for a missing explorer, a city's ragpickers getting their work back.</span></p>
      </div>
      <div class="portrait">{img(p, "portrait", "Black and white portrait of Samuel T Sawian seated by a window", lazy=False, sizes="(max-width: 900px) 300px, 380px", hi=True)}</div>
    </div>
  </section>

  <section class="section" aria-labelledby="work-title">
    <div class="wrap">
      <div class="section-head">
        <h2 id="work-title">Selected work</h2>
        <p>Live-service games with millions of players, a serious game for a Fortune 500 client, and product design for social impact and Meghalayan craft.</p>
      </div>
      <div class="work-grid">{grid}</div>
      <div class="actions" style="margin-top:clamp(40px,6vw,64px)">
        <a class="btn solid" href="{L(p, "games/")}">All games</a>
        <a class="btn" href="{L(p, "product/")}">All product work</a>
      </div>
    </div>
  </section>


  <section class="proof" aria-labelledby="proof-title">
    <h2 id="proof-title" class="visually-hidden">By the numbers</h2>
    <div class="stats">
      <div class="stat"><b>40M</b><span>Monthly active users at FarmVille 2's peak</span></div>
      <div class="stat"><b>1M</b><span>Daily active users on Bingo Bash</span></div>
      <div class="stat"><b>$165M</b><span>Bingo Bash studio acquisition by GSN</span></div>
      <div class="stat"><b>2010</b><span>Building games since</span></div>
    </div>
  </section>

  <section class="section product-zone" aria-labelledby="about-title">
    <div class="wrap teaser">
      <div>
        <span class="label">About</span>
        <h2 id="about-title" style="margin-top:14px">Game producer, product manager, LiveOps lead.</h2>
        <div class="lead prose"><p>Senior Producer and Product Manager, running live, free-to-play games and digital products end-to-end since 2010. I lead distributed, multi-disciplinary teams — engineering, QA, art, sound, localisation — through full production pipelines, using Agile and Waterfall to keep delivery on track. My background also spans LiveOps and post-launch optimisation on high-revenue titles.</p><p>On weekends, you'll find me foraging for lost stories, old forests, and forgotten places.</p></div>
        <div class="actions" style="margin-top:28px"><a class="btn" href="{L(p, "about/")}">Experience, awards &amp; talks</a></div>
      </div>
      <ul class="roles" aria-label="Current roles">
        <li><b>Product Manager</b><span>Dentira · Apr 2025 – present</span></li>
        <li><b>CEO &amp; Co-founder</b><span>Barking Deer Entertainment · 2018 – present</span></li>
        <li><b>Visiting Faculty</b><span>National Institute of Design · 2024 – 2025</span></li>
      </ul>
    </div>
  </section>'''

# ---------- games index
def spread(p, slug, label, title, summary, role, image, alt, b="", flip=False):
    return f'''<article class="project{" flip" if flip else ""}">
        <div class="p-text">
          <span class="label">{label}</span>
          <h2 class="h3like"><a href="{L(p, f"games/{slug}/")}" style="text-decoration:none">{title}</a></h2>
          <p class="summary">{summary}</p>
          {facts([("Role", role)])}
          <div class="actions"><a class="btn" href="{L(p, f"games/{slug}/")}" aria-label="View project: {esc(title)}">View project</a></div>
        </div>
        <div class="p-media"><a href="{L(p, f"games/{slug}/")}" tabindex="-1" aria-hidden="true"><div class="blob {b}">{img(p, image, alt)}</div></a></div>
      </article>'''

def games_body(p):
    return f'''<section class="section" style="padding-top:clamp(28px,5vw,56px)">
    <div class="wrap">
      <div class="section-head">
        <h1>Game design</h1>
        <p>Live-service hits, casino and card games with millions of players, a serious game for a Fortune 500 client, and the indie projects where it started.</p>
      </div>
      {spread(p, "bingo-bash", "GSN Games · 2013 – 2015", "Bingo Bash", "A bingo hall for millions. The world's #1 free-to-play bingo game, top 10 grossing on iTunes two years running and acquired by GSN for $165M.", "Associate Game Producer &amp; Designer", "bingo", "Bingo Bash key art with themed bingo rooms")}
      {spread(p, "farmville-2", "Zynga · 2015 – 2016", "FarmVille 2", "Forty million farmers, a move from San Francisco to India, and the first rooster in FarmVille's history.", "Game Features and Content Producer", "farmville", "FarmVille 2 key art: a farm scene with animals", "b2", True)}
      {spread(p, "teen-patti-gold", "Moonfrog Labs · 2017", "Teen Patti Gold", "The card game of Diwali tables, carried onto phones for more than 4M monthly players.", "Game Producer", "teenpatti", "Teen Patti Gold table with players around a card game", "b3")}
      {spread(p, "dr-nero", "Tata Interactive Systems · 2012 – 2013", "The Curious Case of Dr Nero", "How do you teach senior scientists to share what they know? Send them to an alien planet.", "Senior Game Designer", "nero-1", "Dr Nero gameplay: an isometric alien jungle", "b2", True)}

      <a class="band" href="{L(p, "games/gameloft/")}" style="text-decoration:none">
        {img(p, "avatar", "", sizes="100vw")}
        <div class="band-inner">
          <div>
            <span class="label">Gameloft · 2011 – 2012 · Game Producer</span>
            <h2 class="h3like" style="margin-top:12px">Gameloft</h2>
            <p class="muted" style="margin-top:8px;max-width:48ch">Mobile titles including Asphalt, Assassin's Creed, Spider-Man and James Cameron's Avatar, the world's first stereoscopic 3D game.</p>
            <span class="btn" style="margin-top:18px">View project</span>
          </div>
        </div>
      </a>

      <div class="more" style="margin-top:clamp(40px,6vw,72px)">
        <h2 class="label" style="margin-bottom:28px">More games</h2>
        <div class="cards">
          <article class="card">
            <div class="blob b2">{img(p, "kitty", "Kitty Journey key art: a cartoon cat beside a farmhouse", cls="zoom", sizes="(max-width: 900px) 100vw, 33vw")}</div>
            <span class="meta">V11 Studio · 2016 – 2017</span>
            <h3>Kitty Journey</h3>
            <p>A mobile puzzle game launched as in-house IP, reaching 250,000 downloads in three months. Game Producer, on Android and iOS.</p>
          </article>
          <article class="card">
            <a href="{L(p, "games/stellar-forever/")}" tabindex="-1" aria-hidden="true"><div class="blob">{img(p, "stellar", "Stellar Forever: the heroine fights a giant Octosaurus Rex", sizes="(max-width: 900px) 100vw, 33vw")}</div></a>
            <span class="meta">Vancouver Film School · PC &amp; Xbox</span>
            <h3><a href="{L(p, "games/stellar-forever/")}" style="text-decoration:none">Stellar Forever</a></h3>
            <p>A 2D side-scrolling brawler in outer space. A 19-year-old crashes a royal wedding, then fights hammerhead shark gangs and a giant Octosaurus Rex to escape the Forbidden Kingdom. Game Designer and Programmer.</p>
            <div class="actions"><a class="btn" href="{L(p, "games/stellar-forever/")}" aria-label="View project: Stellar Forever">Trailer &amp; spotlight</a></div>
          </article>
          <article class="card">
            <div class="blob b3">{img(p, "beaver", "Die Beaver Die: a gnome pirate's machine rolls through a valley", cls="zoom", sizes="(max-width: 900px) 100vw, 33vw")}</div>
            <span class="meta">Vancouver Film School · PC</span>
            <h3>Die Beaver Die</h3>
            <p>A reverse tower defence game. Play a gnome pirate hunting a giant magical beaver, collecting magical creations that fuel his machine and its weapons. Game Designer and Programmer.</p>
          </article>
        </div>
      </div>
    </div>
  </section>'''

# ---------- game detail pages
def game_head(p, label, title, summary, rows, links, image, alt, b="", icon=None):
    ic = f'<img class="icon" src="{p.root}assets/img/{icon}.webp" alt="" width="{SIZES[icon+".webp"][0]}" height="{SIZES[icon+".webp"][1]}">' if icon else ""
    return f'''<header class="page-head wrap">
    <div class="p-text">
      <span class="label">{label}</span>
      <h1>{title}</h1>
      <p class="summary">{summary}</p>
      {facts(rows)}
      {play(links)}
    </div>
    <div class="p-media"><div class="blob {b}">{img(p, image, alt, cls="zoom", lazy=False, hi=True)}</div>{ic}</div>
  </header>'''

def bingo_body(p):
    return game_head(p, "GSN Games · 2013 – 2015", "Bingo Bash", "A room full of strangers, a caller, and the hope that the next number is yours. Bingo Bash put that room online.",
        [("Role", "Associate Game Producer &amp; Designer"), ("Genre", "Social Casino"), ("Platform", "Facebook, Android, iOS")],
        PLAY["bingo-bash"], "bingo", "Bingo Bash key art with themed bingo rooms") + f'''
  <div class="wrap page-body">
    <section class="cols">
      <h2>The story</h2>
      <div class="prose"><p>Bingo is one of the oldest social games there is. Bingo Bash took the bingo hall online and became the world's #1 free-to-play bingo game, one of the ten highest-grossing apps on iTunes two years running.</p><p>My job was to keep the hall full and lively: fresh content every cycle, sales and campaigns across Facebook, Android and iOS, and features that gave players a reason to come back the next day.</p></div>
    </section>
    <section class="cols">
      <h2>Results</h2>
      {bullets(["Top 10 overall grossing app on iTunes in <strong>2013</strong> and <strong>2014</strong>",
                "Around <strong>4M</strong> monthly active users, <strong>1M</strong> daily, and more than <strong>$1M</strong> monthly revenue",
                "Feature design that lifted the monthly revenue baseline by <strong>30%</strong>",
                "Quarterly Performance Award, June 2014",
                "Part of the growth phase that led to GSN's <strong>$165M</strong> acquisition in 2014"])}
    </section>
    <section class="cols">
      <h2>Production</h2>
      <div class="prose"><p>Ran content production for the game and managed sales and campaigns across Facebook, Android and iOS, along with in-game copy and the social media community.</p><p>Planned and delivered the product roadmap on a regular deployment cycle, shipping retention and LiveOps features.</p></div>
    </section>
    <section class="cols">
      <h2>Design</h2>
      <div class="prose"><p>Conceived and maintained the game design documents for Bingo Bash's trademarked mechanics.</p><p>Wrote specs, including UI and UX design, for cross-platform features aimed at retention and acquisition.</p></div>
    </section>
  </div>
  {next_links(p, GAMES, "games")}'''

def farmville_body(p):
    return game_head(p, "Zynga · 2015 – 2016", "FarmVille 2", "Forty million people tended farms in FarmVille 2. I helped bring the game's home from San Francisco to India, and gave its farms their first rooster.",
        [("Role", "Game Features and Content Producer"), ("Genre", "Simulation and Role Playing"), ("Platform", "Facebook")],
        PLAY["farmville-2"], "farmville", "FarmVille 2 key art: a farm scene with animals and giant pumpkins", "b2", "farmville-icon") + f'''
  <div class="wrap page-body">
    <section class="cols">
      <h2>Results</h2>
      {bullets(["All-time high of <strong>40M</strong> monthly active users",
                "Grew daily active users by <strong>300,000</strong> through content and optimisation",
                "Introduced the first rooster in FarmVille's history: the Amazing Rooster, leader of the farm animals",
                "Zynga Green Beret Award for that growth, February 2016",
                "Zynga Samurai Award for transitioning FarmVille 2 to India, December 2015"])}
    </section>
    <section class="cols">
      <h2>The work</h2>
      <div class="prose"><p>Joined the core team that transitioned FarmVille 2 from Zynga's San Francisco studio to India.</p><p>Ran the content team and defined a five-year product vision for the game.</p></div>
    </section>
    <section class="case" aria-labelledby="rooster-title" style="padding-bottom:0">
      <div class="cols">
        <div class="block">
          <span class="label">Feature case study</span>
          <h2 id="rooster-title">The first rooster in FarmVille</h2>
          {facts([("Event", "Rooster Coop, an Adoption Quest"), ("Live", "14 June – 15 July 2016"), ("Stages", "Collection, Hatching, Feeding"), ("Reward", "The Amazing Rooster")])}
        </div>
        <div class="prose">
          <p>Every FarmVille farm had its hens, its cows and its sheep. In all the years of the game, not one had ever had a rooster.</p>
          <p>I introduced the first: the Amazing Rooster, leader of the farm animals. He wasn't handed out. He arrived in June 2016 through the Rooster Coop, a month-long Adoption Quest, and players had to raise him themselves, from egg to chick to rooster, before time ran out.</p>
          <p>Each of the three stages leaned on a different part of the farm. Raising animals came first, then harvesting, then crafting, so the whole farm played a part in bringing him home.</p>
        </div>
      </div>

      <div class="stage">
        <figure class="shot">{img(p, "fv-rooster-collection", "Rooster Coop, Collection stage: five baby chickens to feed with Baby Bottles, and an egg tray filling up toward a Rooster egg", cls="zoom", sizes="(max-width: 900px) 100vw, 58vw")}</figure>
        <div class="block">
          <span class="label">Stage 1 · Collection</span>
          <h3>It starts with the hens</h3>
          <div class="prose">
            <p>Players raise baby chickens five at a time, feeding each one Baby Bottles until it grows up. Some need one bottle, some need five, and the hungrier chicks pay back more.</p>
            <p>Every chicken that reaches adulthood drops a prize, such as Speed-Grow, Fertilizer, Water or Super Feed, and lays a special egg. Nine special eggs earn a Rooster egg to hatch.</p>
          </div>
        </div>
      </div>

      <div class="stage flip">
        <figure class="shot">{img(p, "fv-rooster-hatching", "Rooster Coop, Hatching stage: a hen on a straw grid, her egg a few squares away, and a tuning fork meter at 0 of 1,500", cls="zoom", sizes="(max-width: 900px) 100vw, 58vw")}</figure>
        <div class="block">
          <span class="label">Stage 2 · Hatching</span>
          <h3>Bringing the hen to her egg</h3>
          <div class="prose">
            <p>A Rooster egg needs its mother. The hen has to be coaxed across the coop to it, and the one thing that moves her is worms.</p>
            <p>Players fill a tuning fork by harvesting crops and raising and feeding animals. When the fork is full, it charms the worms out of the ground and the hen steps closer. When she reaches the egg, it hatches.</p>
          </div>
        </div>
      </div>

      <div class="stage">
        <figure class="shot">{img(p, "fv-rooster-feeding", "Rooster Coop, Feeding stage: the rooster chick beside a grain bucket at 6 of 300, with six tasks for crafting and harvesting", cls="zoom", sizes="(max-width: 900px) 100vw, 58vw")}</figure>
        <div class="block">
          <span class="label">Stage 3 · Feeding</span>
          <h3>Raising the chick</h3>
          <div class="prose">
            <p>The chick is hungry, and it takes 300 Rooster Grain to raise him. Players earn it from a board of six tasks: watering, fertilizing and harvesting crops, crafting items, and asking friends for help.</p>
            <p>This was the longest stretch of the quest. Some tasks asked for 98 crafts or a couple of hundred crops, and seeing them through was what turned a chick into a leader.</p>
          </div>
        </div>
      </div>

      <div class="stage flip">
        <figure class="shot coop">{img(p, "fv-rooster-coop", "The finished Rooster Coop on a farm: a blue and white coop with a fenced yard", cls="zoom", sizes="(max-width: 900px) 100vw, 371px")}</figure>
        <div class="block">
          <span class="label">The reward</span>
          <h3>The leader of the farm</h3>
          <div class="prose">
            <p>When the last of the grain is in, the chick grows into the Amazing Rooster and takes his place in the coop. Then he gets to work.</p>
          </div>
          {bullets(["He raises the farm's water capacity by <strong>10</strong>, from 30 to 40, for <strong>28 days</strong>",
                    "He waters your trees and groves",
                    "When his watering uses run out, one click has him feed every adult chicken on your main farm, once every <strong>24 hours</strong>",
                    "Players who wanted him to stay longer could extend his visit for 15 Farmbucks"])}
        </div>
      </div>

      <div class="cols">
        <h3 class="col-head">The launch</h3>
        <div class="prose"><p>Zynga announced him with a trailer, "Get the Amazing Rooster!" Before long, players were filming their own hunts for Rooster Eggs.</p></div>
      </div>
      <div class="videos">
        {video("3iTk1hW5USY", "Get the Amazing Rooster! (FarmVille 2)", "Official trailer · FarmVille 2")}
        {video("jzISFSoFQ7I", "FarmVille 2 ep. 128: The hunt for Rooster Eggs", "Gameplay · Player video by Gao AsaurusG")}
      </div>
      <p class="meta"><a href="https://farmville2.fandom.com/wiki/Rooster_Coop" target="_blank" rel="noopener" style="color:inherit">Rooster Coop on the FarmVille 2 wiki ↗</a></p>
    </section>
  </div>
  {next_links(p, GAMES, "games")}'''

def teenpatti_body(p):
    return game_head(p, "Moonfrog Labs · 2017", "Teen Patti Gold", "The card game of Indian family gatherings, carried onto phones and played by more than five crore people.",
        [("Role", "Game Producer"), ("Genre", "Card Game, Casino"), ("Platform", "Android, iOS")],
        PLAY["teen-patti-gold"], "teenpatti", "Teen Patti Gold table with players around a card game", "b3", "teenpatti-icon") + f'''
  <div class="wrap page-body">
    <section class="cols">
      <h2>The story</h2>
      <div class="prose"><p>Teen Patti has been dealt at Diwali tables for generations. Teen Patti Gold brought that table to phones, and it became one of India's top-grossing mobile card games.</p><p>I worked on what kept people at the table: VIP subscriptions, retention systems, and a web version so the game could follow players beyond their phones.</p></div>
    </section>
    <section class="cols">
      <h2>Results</h2>
      {bullets(["More than <strong>4M</strong> monthly active users", "Around <strong>$250k</strong> monthly revenue",
                "Moonfrog was acquired for <strong>$90M</strong> in December 2021"])}
    </section>
    <section class="cols">
      <h2>The work</h2>
      <div class="prose"><p>Supported development of VIP subscription features for a top-grossing mobile card game.</p><p>Worked on retention systems and player experience improvements, and helped build and launch the web version with an external development team.</p></div>
    </section>
  </div>
  {next_links(p, GAMES, "games")}'''

def nero_body(p):
    return game_head(p, "Tata Interactive Systems · 2012 – 2013", "The Curious Case of Dr Nero",
        "How do you teach senior scientists to share what they know? We sent them to an alien planet.",
        [("Role", "Senior Game Designer"), ("Genre", "Role Playing Game"), ("Platform", "PC")], [],
        "nero-1", "Dr Nero gameplay: an isometric alien jungle with a mission dialogue") + f'''
  <div class="wrap page-body">
    <section class="two">
      <div class="block">
        <h2>The challenge</h2>
        <div class="prose"><p>Change how employees behave, from hoarding knowledge to sharing it. The game had to be non-violent and appeal to players aged 30 to 60.</p><p>The audience was senior research scientists who were tired of traditional training.</p></div>
      </div>
      <div class="block">
        <h2>The solution</h2>
        <div class="prose"><p>Players take the role of a scientist on an alien planet, retracing the research of a missing explorer, Dr Nero.</p><p>The game recreates real DNA research so it rings true to scientists, and progress depends on working with fellow scientists.</p></div>
      </div>
    </section>
    <section class="block" aria-label="Screenshots">
      <div class="shots">
        {img(p, "nero-2", "Dr Nero: mission screen over the jungle map", cls="zoom", sizes="(max-width: 900px) 50vw, 25vw")}
        {img(p, "nero-3", "Dr Nero: level select over the island", cls="zoom", sizes="(max-width: 900px) 50vw, 25vw")}
        {img(p, "nero-4", "Dr Nero: rocky outcrop on the alien island", cls="zoom", sizes="(max-width: 900px) 50vw, 25vw")}
        {img(p, "nero-1", "Dr Nero: river crossing with the research log open", cls="zoom", sizes="(max-width: 900px) 50vw, 25vw")}
      </div>
    </section>
    <section class="cols">
      <h2>Acclaim</h2>
      <div class="block">
        <p class="pull">Built as a single-player game, it was rated so highly by the client that it was later converted to multiplayer.</p>
        {bullets(["Best E-learning Game: Gold Medal in Design, LearnX Asia Pacific, May 2013",
                  "Best Use of Games and Simulations for Learning: Bronze, Brandon Hall Excellence Awards, September 2013",
                  "Excellence in Learning: Bronze, Brandon Hall Excellence Awards, October 2013"])}
      </div>
    </section>
    <section class="cols">
      <h2>The role</h2>
      <div class="prose"><p>Designed role-playing, alternate reality and behaviour-change games as learning solutions for Fortune 500 companies, pitching proposals and demos to senior management and CXOs.</p><p>Built rapid prototypes and game design documents, modelled level design and game architecture, and led a design team from prototype through alpha, beta and gold.</p></div>
    </section>
  </div>
  {next_links(p, GAMES, "games")}'''

def gameloft_body(p):
    icons = [("gl-spiderman", "Spider-Man icon"), ("gl-assassins", "Assassin's Creed icon"), ("gl-avatar", "James Cameron's Avatar cover"),
             ("gl-asphalt6", "Asphalt 6 icon"), ("gl-asphalt5", "Asphalt 5 icon"), ("gl-settlers", "Gameloft title icon"), ("gl-modernwarfare", "Modern Warfare icon")]
    ic = "".join(f'<img src="{p.root}assets/img/{n}.webp" alt="{a}" width="{SIZES[n+".webp"][0]}" height="{SIZES[n+".webp"][1]}" loading="lazy" decoding="async">' for n, a in icons)
    return game_head(p, "Gameloft · 2011 – 2012", "Gameloft", "Console-sized adventures, made to fit in a pocket.",
        [("Role", "Game Producer"), ("Genre", "Various"), ("Platform", "Android, iOS")], [],
        "avatar", "James Cameron's Avatar game art: a Na'vi warrior in the jungle") + f'''
  <div class="wrap page-body">
    <section class="cols">
      <h2>The story</h2>
      <div class="prose"><p>In the early 2010s, Gameloft was putting big-screen adventures on phones: street racing in Asphalt, rooftops in Assassin's Creed, web-slinging in Spider-Man, and James Cameron's Avatar, the world's first stereoscopic 3D game.</p><p>This is where I learned to produce. I steered teams of more than fifty developers, designers and testers across continents, keeping very different games on course at the same time.</p></div>
    </section>
    <section class="cols">
      <h2>Games</h2>
      <div class="block">
        {bullets(["Asphalt 5, 6 &amp; 7", "Assassin's Creed: Altaïr's Chronicles", "James Cameron's Avatar", "The Settlers", "Modern Warfare", "Spider-Man"])}
        <div class="icons" style="grid-template-columns:repeat(auto-fill,56px)">{ic}</div>
      </div>
    </section>
    <section class="cols">
      <h2>The role</h2>
      <div class="prose"><p>Led several development teams to complete top-tier mobile titles, managing more than 50 onshore and offshore developers, designers and QA testers.</p><p>Worked with offshore senior executives and business partners on design requirements, progress updates and added features.</p></div>
    </section>
    <section aria-label="Asphalt 6 key art">{img(p, "asphalt6", "Asphalt 6: Adrenaline key art", cls="zoom", sizes="100vw", style="border-radius:20px;width:100%")}</section>
  </div>
  {next_links(p, GAMES, "games")}'''

def stellar_body(p):
    return game_head(p, "Vancouver Film School", "Stellar Forever",
        "A royal wedding, a gatecrasher, and a giant Octosaurus Rex. A 2D side-scrolling brawler set in outer space.",
        [("Role", "Game Designer &amp; Programmer"), ("Genre", "RPG side-scrolling brawler"), ("Platform", "PC, Xbox")], [],
        "stellar", "Stellar Forever: the heroine fights a giant Octosaurus Rex", "b2") + f'''
  <div class="wrap page-body">
    <section class="cols">
      <h2>The game</h2>
      <div class="prose"><p>You play a 19-year-old girl who crashes a royal wedding. To find her way out of the Forbidden Kingdom she has to battle hammerhead shark gangs and a giant Octosaurus Rex.</p></div>
    </section>
    <section class="block" aria-labelledby="videos-title">
      <h2 id="videos-title">Videos</h2>
      <div class="videos">
        {video("L5y-jxZg7fs", "Stellar Forever trailer", "Gameplay trailer")}
        {video("r4likTtedFY", "The Blast Light: Stellar Forever", "Media spotlight · Vancouver Film School")}
      </div>
    </section>
  </div>
  {next_links(p, GAMES, "games")}'''

# ---------- product index
def product_body(p):
    return f'''<section class="section product-zone" style="padding-top:clamp(28px,5vw,56px)">
    <div class="wrap">
      <div class="section-head">
        <h1>Product design</h1>
        <p>Procurement software for dental groups, an app that put Mumbai's ragpickers back to work, a brand for Meghalaya's finest produce, and websites for schools and hospitals in Shillong.</p>
      </div>
      <article class="project">
        <div class="p-text">
          <span class="label">SaaS · Procurement &amp; accounts payable</span>
          <h2 class="h3like">Dentira</h2>
          <p class="summary">A dental group can run hundreds of clinics, each ordering supplies from dozens of vendors, and every delivery brings an invoice. Dentira brings the buying and the paying into one place, and some of the largest dental groups use it to run their procurement.</p>
          <div class="prose">
            <p>I own live product delivery: the roadmap, sprint planning and releases, working with design and engineering on how the workflows behave.</p>
            <p>Much of my work sits in the invoice lifecycle: approvals, sending invoices back for correction, bulk actions, role-based permissions, and syncing to accounting systems. I started with a full UX audit and turned it into personas, interactive mockups and a phased improvement plan.</p>
          </div>
          {facts([("Role", "Product Manager"), ("Since", "April 2025"), ("Users", "Dental support organisations")])}
        </div>
        <div class="p-media">
          <figure class="flow" aria-label="The invoice journey in Dentira">
            <ol>
              <li><b>Order</b><span>Real-time catalogues and pricing from many vendors, in one place</span></li>
              <li><b>Receive</b><span>Deliveries are checked in at the clinic</span></li>
              <li><b>Match</b><span>Invoices are read automatically and matched to the order and delivery</span></li>
              <li class="loop"><b>Approve</b><span>The right people sign off, by role</span><em>or send back for correction</em></li>
              <li><b>Sync</b><span>Approved invoices flow to accounting</span></li>
            </ol>
            <figcaption>The invoice journey</figcaption>
          </figure>
        </div>
      </article>
      <article class="project">
        <div class="p-text">
          <span class="label">UX &amp; UI · Branding · Android</span>
          <h2 class="h3like"><a href="{L(p, "product/recycled-earth/")}" style="text-decoration:none">Recycled Earth</a></h2>
          <p class="summary">A mobile app to schedule and track how household waste is picked up, processed and disposed of. Featured by UNICEF.</p>
          {facts([("Scale", "22,000+ families, 12+ routes")])}
          <div class="actions"><a class="btn" href="{L(p, "product/recycled-earth/")}" aria-label="Read case study: Recycled Earth">Read case study</a></div>
        </div>
        <div class="p-media"><a href="{L(p, "product/recycled-earth/")}" tabindex="-1" aria-hidden="true"><div class="blob">{img(p, "re-challenge", "Women sorting plastic waste in a recycling shed")}</div></a></div>
      </article>
      <article class="project flip">
        <div class="p-text">
          <span class="label">Brand · Product · Print &amp; packaging</span>
          <h2 class="h3like"><a href="{L(p, "product/meghalayan-age/")}" style="text-decoration:none">Meghalayan Age</a></h2>
          <p class="summary">Brand identity, store and packaging for a Government of Meghalaya initiative promoting the state's produce and crafts.</p>
          {facts([("Range", "30+ food products")])}
          <div class="actions"><a class="btn" href="{L(p, "product/meghalayan-age/")}" aria-label="Read case study: Meghalayan Age">Read case study</a></div>
        </div>
        <div class="p-media"><a href="{L(p, "product/meghalayan-age/")}" tabindex="-1" aria-hidden="true"><div class="blob b2">{img(p, "ma-store-1", "Meghalayan Age store interior with textiles and crafts")}</div></a></div>
      </article>
      <section class="more" aria-labelledby="sites-title" style="margin-bottom:clamp(48px,7vw,80px)">
        <h2 id="sites-title" class="label" style="margin-bottom:28px">Websites</h2>
        <div class="sites">
          <article>
            <span class="meta">Designed &amp; built</span>
            <h3>Happy Feet School</h3>
            <p>A playschool in Shillong that has taught three-to-five-year-olds through play since 2012. The site carries that warmth: bright photography, its Nursery and Lower KG programmes, admissions, a gallery of school life, and a decade of letters from parents.</p>
            <a class="btn" href="https://happyfeetshillong.com/" target="_blank" rel="noopener">happyfeetshillong.com<span class="visually-hidden"> (opens in a new tab)</span><span aria-hidden="true">↗</span></a>
          </article>
          <article>
            <span class="meta">Built</span>
            <h3>Supercare Hospital</h3>
            <p>A 150-bed multi-speciality hospital in Shillong. The site helps patients find a doctor, book an appointment and reach emergency care quickly, and lays out the hospital's specialities, services and visiting rules.</p>
            <a class="btn" href="https://supercarehospital.com/" target="_blank" rel="noopener">supercarehospital.com<span class="visually-hidden"> (opens in a new tab)</span><span aria-hidden="true">↗</span></a>
          </article>
          <article>
            <span class="meta">Designed</span>
            <h3>Bethany Hospitals</h3>
            <p>A hospital network founded in Shillong in 2002, with branches across Meghalaya and its own nursing school. The site brings 22 specialities, four locations, doctor search, health packages and patient guides into one clear structure.</p>
            <a class="btn" href="https://bethanyhospitals.com/" target="_blank" rel="noopener">bethanyhospitals.com<span class="visually-hidden"> (opens in a new tab)</span><span aria-hidden="true">↗</span></a>
          </article>
        </div>
      </section>
      <div class="more">
        <h2 class="label" style="margin-bottom:28px">Other product work</h2>
        <div class="others">
          <article>
            <span class="meta">Healthcare platform · COVID response</span>
            <h3>nULTA</h3>
            <p>Turned a fragmented doctor marketplace into a guided healthcare platform with clearer patient journeys. Shipped an AI-assisted triage flow, with GP oversight, that routes patients to the right specialist. Incentive-aligned participation and standard onboarding scaled the network to 1,000+ doctors, with pharmacy-recognised prescriptions and subscription check-ups.</p>
          </article>
          <article>
            <span class="meta">Cultural media platform</span>
            <h3>7 Sisters Kitchen</h3>
            <p>A cultural media platform pairing a recipe repository with documentary content. Helped plan and produce the food documentaries, which have drawn tens of thousands of views on YouTube.</p>
          </article>
        </div>
      </div>
    </div>
  </section>'''

def phone(p, name, alt, cap):
    return f'<figure class="phone" style="margin:0">{img(p, name, alt, cls="zoom", sizes="132px")}<figcaption>{cap}</figcaption></figure>'

def re_body(p):
    return f'''<header class="page-head wrap">
    <div class="p-text">
      <span class="label">UX &amp; UI · Branding · Android</span>
      <h1>Recycled Earth</h1>
      <p class="summary">When Mumbai changed how it collected its rubbish, the ragpickers who sorted it lost their work. Recycled Earth gave it back, with an app to run every pickup.</p>
      {facts([("Roles", "UX and UI design, Branding and Identity"), ("Platform", "Android"), ("Instagram", "@therecycledearth")])}
    </div>
    <div class="p-media" style="display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:12px;align-items:center">
      {img(p, "re-poster-50", "Recycled Earth post: 50 tons of waste collected in November 2021", cls="zoom", lazy=False, hi=True, sizes="(max-width: 900px) 50vw, 30vw", style="border-radius:16px")}
      {img(p, "re-poster-60k", "Recycled Earth post: 60,000 families took part", cls="zoom", lazy=False, sizes="(max-width: 900px) 50vw, 30vw", style="border-radius:16px")}
    </div>
  </header>
  <div class="wrap page-body">
    <div class="stats-inline">
      <div><b>800–1,200 kg</b><span>Plastic waste collected from one route</span></div>
      <div><b>22,000+</b><span>Families coordinated by 950 members in Maharashtra</span></div>
      <div><b>70–90 L</b><span>Poly fuel produced</span></div>
      <div><b>12+</b><span>Routes, and growing</span></div>
    </div>
    <section class="case-head">
      <div class="block">
        <h2>The challenge</h2>
        <div class="prose"><p>Mumbai's residents throw unsorted waste, plastics included, into public bins. Ragpickers used to collect, sort and sell the recyclables from those bins.</p><p>Changes to municipal collection were costing ragpickers their livelihoods and leaving waste unsorted. Trucks carried it straight to low-lying landfills, where it polluted the ground and created health risks.</p></div>
      </div>
      <div class="blob b2" style="aspect-ratio:4/3">{img(p, "re-challenge", "Two women sorting plastic waste in a recycling shed", cls="zoom")}</div>
    </section>
    <section class="block">
      <h2>The solution</h2>
      <div class="prose" style="max-width:none;grid-template-columns:repeat(auto-fit,minmax(min(100%,260px),1fr));gap:12px 40px">
        <p>A poly-fuel processing facility in Thane, fed by collection trucks gathering unsorted waste.</p>
        <p>The same ragpickers, now employed in a safe, sanitary space to separate plastic from organic waste.</p>
        <p>Plastic turned into poly fuel; organic waste composted into a garden and community space at the facility.</p>
        <p>The Recycled Earth app to monitor every pickup and every stage of processing.</p>
      </div>
    </section>
    <section class="cols">
      <h2>My role</h2>
      {bullets(["Co-owned product vision and delivery for a platform with many stakeholders",
                "Designed progress and contribution systems, borrowed from games, to encourage participation and accountability",
                "Delivered GPS tracking, scheduling and impact dashboards across the resident, driver and admin apps",
                "Designed the Recycled Earth brand and identity"])}
    </section>
    <section class="block">
      <h2>How a route runs</h2>
      <ol class="steps">
        <li><b>01</b><span>On pickup day, trucks leave the facility on their set routes.</span></li>
        <li><b>02</b><span>Building societies and residents get pickup notifications and a live ETA.</span></li>
        <li><b>03</b><span>Waste is collected from designated points.</span></li>
        <li><b>04</b><span>Waste reaches the sorting facility, ready to be separated.</span></li>
      </ol>
    </section>
    <section class="users" aria-labelledby="users-title">
      <h2 id="users-title" style="font-size:var(--fs-l)">Three users, three versions of the app</h2>
      <div class="user">
        <div><h3 style="font-size:var(--fs-m);margin-bottom:10px">Residents</h3><div class="prose"><p>People living in building societies registered with Recycled Earth. They see pickup schedules, track the truck down to the minute, and read waste and recycling tips.</p></div></div>
        <div class="phones" tabindex="0" aria-label="Resident app screens, scrollable">
          {phone(p, "re-res-login", "Resident app login screen", "Log in")}{phone(p, "re-res-home", "Resident landing page with pickup status", "Landing")}{phone(p, "re-res-schedule", "Resident pickup schedule", "Pickup schedule")}{phone(p, "re-res-track", "Live truck tracking map", "Truck tracking")}{phone(p, "re-res-pickup", "Landing page with a pickup scheduled", "Pickup scheduled")}
        </div>
      </div>
      <div class="user">
        <div><h3 style="font-size:var(--fs-m);margin-bottom:10px">Pickup drivers</h3><div class="prose"><p>The most minimal version of the app. Drivers see their route and every pickup on it. GPS units on trucks gifted by the municipality make live tracking possible.</p></div></div>
        <div class="phones">{phone(p, "re-drv-home", "Driver landing page with today's trips", "Trips")}{phone(p, "re-map", "Driver route map", "Route")}</div>
      </div>
      <div class="user">
        <div><h3 style="font-size:var(--fs-m);margin-bottom:10px">Admins</h3><div class="prose"><p>Admins add routes and pickup points, track every truck across routes, and manage the housing societies on each route.</p></div></div>
        <div class="phones" tabindex="0" aria-label="Admin app screens, scrollable">
          {phone(p, "re-adm-home", "Admin landing page with route management", "Landing")}{phone(p, "re-adm-route", "Active truck tracking on a route", "Truck tracking")}{phone(p, "re-adm-pickups", "Pickup point management", "Pickups")}{phone(p, "re-adm-users", "Pickup point requests from users", "Users")}{phone(p, "re-adm-new", "Adding a new route", "New route")}
        </div>
      </div>
    </section>
    <section class="acclaim">
      <div class="block">
        <h2>Acclaim</h2>
        <p class="pull">Featured as a best-practice success story in UNICEF's WASH-Action4Change newsletter, March 2022.</p>
      </div>
      <div class="pages">
        {"".join(img(p, n, a, cls="zoom", sizes="(max-width: 900px) 33vw, 12vw") for n, a in [("re-unicef", "UNICEF WASH-Action4Change feature cover"), ("re-unicef-1", "Newsletter page 1"), ("re-unicef-2", "Newsletter page 2"), ("re-unicef-3", "Newsletter page 3"), ("re-unicef-4", "Newsletter page 4"), ("re-unicef-5", "Newsletter page 5")])}
      </div>
    </section>
  </div>
  {next_links(p, PRODUCTS, "product")}'''

FOOD_ALTS = ["Food line pouch", "Green tea pouch", "Cashew nuts pouch", "Food line pouch", "Food line pouch", "Dried ginger pouch", "Rice pouch",
             "Black sesame pouch", "Food line pouch", "Food line pouch", "Black pepper pouch", "King chilli pouch", "Food line pouch", "Food line pouch",
             "Jam jar", "Jam jar", "Chilli pouch", "Bird's eye chilli pouch", "Coffee pouch", "Coffee pouch", "Foxtail millet pouch", "Food line pouch"]

def ma_body(p):
    food = "".join(img(p, f"ma-food-{i+1:02d}", a, cls="zoom", sizes="220px") for i, a in enumerate(FOOD_ALTS))
    return f'''<header class="page-head wrap">
    <div class="p-text">
      <span class="label">Brand · Product · Print &amp; packaging</span>
      <h1>Meghalayan Age</h1>
      <p class="summary">Meghalaya grows turmeric with the highest curcumin content in the world. Meghalayan Age gave the state's produce a brand worthy of it.</p>
      {facts([("Client", "Government of Meghalaya"), ("Roles", "Brand and Identity Design, Product Design, Creative Direction, Project Management"), ("Platform", "Print and Packaging")])}
    </div>
    <div class="p-media"><div class="blob">{img(p, "ma-store-1", "Meghalayan Age store interior with textiles and crafts", cls="zoom", lazy=False, hi=True)}</div></div>
  </header>
  <div class="wrap page-body">
    <section class="cols">
      <h2>My role</h2>
      {bullets(["Led brand identity, visual design and storytelling for a state-backed cultural platform",
                "Shaped the stories told around indigenous food products and regional heritage",
                "Worked on digital and physical retail, including the New Delhi store",
                "Led the storytelling and photography supporting agro-tourism initiatives"])}
    </section>
    <section class="paper">
      <div class="prose">
        <h2 style="font-size:var(--fs-m);color:#1b1b1b">Branding and logo</h2>
        <p>Meghalaya grows organic food that deserves to be known far beyond the state. The brand had to match the care of the artisans and farmers behind it, and stand for high standards and quality.</p>
        <p>The logo is a monogram of the company's initials, borrowing the confidence of couture fashion marks. Minimal, a little luxurious, a touch bold: simple organic products made to exacting standards.</p>
        <div class="tags"><span>Sophisticated</span><span>Luxurious</span><span>Modern</span><span>Elegant</span><span>Refined</span></div>
        <p style="font-size:var(--fs-s)">Combination mark and wordmark · Black and white</p>
      </div>
      <div class="logo-tile">{img(p, "ma-logo", "Meghalayan Age logo: a mountain monogram with wordmark", sizes="260px", style="max-width:260px")}</div>
    </section>
    <section class="gallery" aria-label="The store">
      {img(p, "ma-store-2", "Meghalayan Age storefront at night", cls="zoom g-a", sizes="(max-width: 900px) 100vw, 40vw")}
      {img(p, "ma-store-3", "Baskets and crafts on store shelves", cls="zoom", sizes="(max-width: 900px) 50vw, 30vw")}
      {img(p, "ma-store-4", "One-year anniversary signage in the store", cls="zoom", sizes="(max-width: 900px) 50vw, 30vw")}
      {img(p, "ma-box-2", "Premium turmeric box, open and closed", cls="zoom", sizes="(max-width: 900px) 100vw, 60vw", style="grid-column:span 2")}
    </section>
    <section class="two">
      <div class="block">
        <h2>The premium food line</h2>
        <div class="prose"><p>Some Meghalayan produce exists nowhere else: Lakadong turmeric, with the highest curcumin content in the world, wild forest honey and white tea.</p><p>The premium range is dressed in black, with gold or silver accents. Indigenous artists drew only the outlines of the turmeric, honey and tea leaves, so the illustrations shimmer like the silver lining of a cloud.</p></div>
      </div>
      <div class="pack">
        {img(p, "ma-box", "Lakadong turmeric premium box packaging", cls="zoom", sizes="(max-width: 900px) 50vw, 25vw")}
        {img(p, "ma-jar", "Lakadong turmeric premium jar with gold monogram lid", cls="zoom", sizes="(max-width: 900px) 50vw, 25vw")}
      </div>
    </section>
    <section class="two">
      <div class="block">
        <h2>The MAL food range</h2>
        <div class="prose"><p>The mid-range packaging is white, with accent colours taken from the food inside each pack. With more than 30 products, white gives the range a softer footprint on the shelf while keeping the brand elegant.</p><p>Every pack carries a hand-drawn illustration of its product by indigenous artists from Meghalaya.</p></div>
      </div>
      <div class="pack">
        {img(p, "ma-mal-1", "MAL range pouch with green leaf illustration", cls="zoom", sizes="(max-width: 900px) 50vw, 25vw", style="aspect-ratio:3/4")}
        {img(p, "ma-mal-2", "MAL bay leaf pouch", cls="zoom", sizes="(max-width: 900px) 50vw, 25vw", style="aspect-ratio:3/4")}
      </div>
    </section>
    <section class="block">
      <h2>The food line</h2>
      <div class="foodline" tabindex="0" aria-label="Food line packaging, scrollable">{food}</div>
    </section>
  </div>
  {next_links(p, PRODUCTS, "product")}'''

# ---------- about
def about_body(p):
    return f'''<section class="wrap about-hero">
    <div>
      <span class="label">Game Producer · Product Manager · LiveOps Lead</span>
      <h1 style="margin-top:14px">About</h1>
      <div class="lead prose"><p>Senior Producer and Product Manager, running live, free-to-play games and digital products end-to-end since 2010. I lead distributed, multi-disciplinary teams — engineering, QA, art, sound, localisation — through full production pipelines, using Agile and Waterfall to keep delivery on track. My background also spans LiveOps and post-launch optimisation on high-revenue titles.</p><p>On weekends, you'll find me foraging for lost stories, old forests, and forgotten places.</p></div>
    </div>
    <div class="portrait">{img(p, "portrait", "Black and white portrait of Samuel T Sawian seated by a window", lazy=False, sizes="(max-width: 900px) 280px, 340px", hi=True)}</div>
  </section>
  <section class="section" style="padding-top:0">
    <div class="wrap">
      <div class="intro">
        <div>
          <h2 class="label">What I do</h2>
          <ul class="chips">
            <li>Product &amp; feature ownership</li><li>LiveOps &amp; post-launch optimisation</li><li>Roadmap planning &amp; prioritisation</li>
            <li>Systems &amp; game design thinking</li><li>Cross-functional leadership</li><li>Delivery, scope &amp; risk management</li>
          </ul>
        </div>
        <div>
          <h2 class="label">Languages</h2>
          <ul class="chips"><li>Khasi</li><li>English</li><li>Hindi</li></ul>
        </div>
      </div>
      <div class="about-grid">
        <div>
          <h2 class="col-head">Experience</h2>
          <ol class="timeline">
            <li><span class="when">Apr 2025 – Present</span><span class="role">Product Manager</span><span class="where">Dentira</span><span class="what">Own live delivery for a workflow-driven SaaS platform: roadmap, sprints and releases, and features across approvals, integrations and automation.</span></li>
            <li><span class="when">Jul 2018 – Present</span><span class="role">CEO &amp; Co-founder</span><span class="where">Barking Deer Entertainment</span><span class="what">A design-led studio making games, products and cultural platforms. Creative direction, production planning and end-to-end delivery.</span></li>
            <li><span class="when">Jan 2024 – Jan 2025</span><span class="role">Visiting Faculty</span><span class="where">National Institute of Design</span><span class="what">Taught the foundations of game mechanics and level design. Mentored final-semester diploma projects and sat on graduation juries.</span></li>
            <li><span class="when">Mar 2023 – Nov 2024</span><span class="role">Business Consultant</span><span class="where">PRIME Entrepreneurship Meghalaya, Government of Meghalaya</span><span class="what">Jury member for the Top 100 Meghalaya Startups 2024, one-to-one mentor for the startup incubator, and workshops on the art of pitching.</span></li>
            <li><span class="when">Apr 2017 – Oct 2017</span><span class="role">Game Producer, <a href="{L(p, "games/teen-patti-gold/")}">Teen Patti Gold</a></span><span class="where">Moonfrog Labs</span><span class="what">VIP subscription features, retention systems, and a web version launched with an external team.</span></li>
            <li><span class="when">Jul 2016 – Jan 2017</span><span class="role">Game Producer, Kitty Journey</span><span class="where">V11 Studio, Mauritius</span><span class="what">Launched in-house IP to 250K downloads in three months, managing external development, QA, sound and localisation teams.</span></li>
            <li><span class="when">Feb 2015 – Jul 2016</span><span class="role">Game Producer, <a href="{L(p, "games/farmville-2/")}">FarmVille 2</a></span><span class="where">Zynga</span><span class="what">Grew daily active users by 300K, led the content team and set a five-year product vision during the move to India.</span></li>
            <li><span class="when">Feb 2013 – Feb 2015</span><span class="role">Associate Game Producer &amp; Designer, <a href="{L(p, "games/bingo-bash/")}">Bingo Bash</a></span><span class="where">Bash Gaming / GSN Games</span><span class="what">Shipped retention and LiveOps features, wrote design docs for trademarked mechanics, and ran content, campaigns and the roadmap through the growth phase to a $165M acquisition.</span></li>
            <li><span class="when">May 2012 – Feb 2013</span><span class="role">Senior Game Designer, Serious Games</span><span class="where">Tata Interactive Systems</span><span class="what">RPGs, alternate reality and behaviour-change games for Fortune 500 clients, including <a href="{L(p, "games/dr-nero/")}">Dr Nero</a>. Pitched to CXOs and led a design team from prototype to gold.</span></li>
            <li><span class="when">Jan 2011 – Jun 2012</span><span class="role">Game Producer</span><span class="where"><a href="{L(p, "games/gameloft/")}">Gameloft</a></span><span class="what">Led 50+ onshore and offshore developers, designers and QA on top-tier mobile titles.</span></li>
          </ol>
        </div>
        <div class="side">
          <div>
            <h2 class="h3like">Education</h2>
            <div class="edu">
              <div><b>PGDP Game Design &amp; Programming</b><span>Vancouver Film School, Canada · 2009 – 2010</span></div>
              <div><b>PGDP New Media Design</b><span>National Institute of Design, Ahmedabad · 2006 – 2009</span></div>
              <div><b>Bachelor of Computer Applications</b><span>Bangalore University · 2002 – 2005</span></div>
              <div><b>High school</b><span>St Edmund's School, Shillong</span></div>
            </div>
          </div>
          <div>
            <h2 class="h3like">Awards</h2>
            <ul class="awards">
              <li><b>Kickstart Grant, Original IP in Production</b><span>PRIME Meghalaya · Jan 2025</span></li>
              <li><b>Action4Change feature, Recycled Earth</b><span>Barking Deer &amp; UNICEF · Mar 2022</span></li>
              <li><b>Green Beret Award</b><span>Zynga · Feb 2016</span></li>
              <li><b>Samurai Award</b><span>Zynga · Dec 2015</span></li>
              <li><b>Winner, Game Design Challenge: Constructive Destruction</b><span>Gamasutra · Jul 2015</span></li>
              <li><b>Quarterly Performance Award</b><span>Bingo Bash · Jun 2014</span></li>
              <li><b>Excellence in Learning: Bronze</b><span>Brandon Hall Excellence Awards, with Tata Interactive Systems · Oct 2013</span></li>
              <li><b>Best Use of Games and Simulations for Learning: Bronze</b><span>Brandon Hall Excellence Awards, with Tata Interactive Systems · Sep 2013</span></li>
              <li><b>Best E-learning Game: Gold Medal in Design</b><span>LearnX Asia Pacific, with Tata Interactive Systems · May 2013</span></li>
            </ul>
          </div>
          <div>
            <h2 class="h3like">Workshops &amp; talks</h2>
            <ul class="awards">
              <li><b>Short Stories in Gahndruk: A Creative Writing Adventure</b><span>Kuhiro Class · Jan 2026</span></li>
              <li><b>Pitch Deck 101</b><span>Rishi Valley School · Sep 2024</span></li>
              <li><b>The Art of Making Games</b><span>Rishi Valley School · Jan 2024</span></li>
              <li><b>Talking Entrepreneurship</b><span>Annual Sawkpoh Durbar · Jan 2023</span></li>
              <li><b>The World of Video Games</b><span>SOS Children's Villages · Dec 2020</span></li>
            </ul>
          </div>
          <div>
            <h2 class="h3like">Contact &amp; links</h2>
            <ul class="awards">
              <li><b><a href="mailto:{EMAIL}">{EMAIL}</a></b><span>Email</span></li>
              <li><b>How a serious game transformed a business</b><span>Publication</span></li>
              <li><b><a href="{BLOG}" target="_blank" rel="noopener">samuelsawian.substack.com</a></b><span>Blog</span></li>
              <li><b><a href="{LINKEDIN}" target="_blank" rel="noopener">linkedin.com/in/samuelsawian</a></b><span>LinkedIn</span></li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </section>'''

def notfound_body(p):
    return f'''<section class="wrap notfound">
    <span class="label">404</span>
    <h1>Page not found.</h1>
    <p class="muted" style="max-width:46ch">The page you were looking for has moved or doesn't exist. Try one of these instead.</p>
    <div class="actions"><a class="btn solid" href="{L(p, "")}">Home</a><a class="btn" href="{L(p, "games/")}">Games</a><a class="btn" href="{L(p, "product/")}">Product</a><a class="btn" href="{L(p, "about/")}">About</a></div>
  </section>'''

# ------------------------------------------------------------------ structured data helpers
def game_ld(name, genre, platforms, store=None, desc=""):
    d = {"@type": "VideoGame", "name": name, "genre": genre, "gamePlatform": platforms, "description": desc}
    if store: d["sameAs"] = store
    return d

def creative_ld(name, desc, kind="CreativeWork"):
    return {"@type": kind, "name": name, "description": desc, "creator": {"@type": "Person", "name": "Samuel T Sawian"}}

def webpage_ld(page, kind="WebPage", extra=None):
    d = {"@type": kind, "name": page.title, "description": page.desc, "inLanguage": "en-IN"}
    if SITE_URL:
        d["url"] = page.abs(); d["isPartOf"] = {"@id": f"{SITE_URL}/#website"}
        d["primaryImageOfPage"] = f"{SITE_URL}/assets/og/{page.og}.jpg"
    if extra: d.update(extra)
    return d

# ------------------------------------------------------------------ pages
HOME_C = [("Home", "")]
G = HOME_C + [("Games", "games/")]
P = HOME_C + [("Product", "product/")]

def build_pages():
    pages = []
    def add(pg, ld): pg.jsonld = ld(pg); pages.append(pg)

    website = lambda pg: ([{"@type": "WebSite", "@id": f"{SITE_URL}/#website", "url": f"{SITE_URL}/", "name": SITE_NAME, "inLanguage": "en-IN", "publisher": {"@id": f"{SITE_URL}/#person"}}] if SITE_URL else [{"@type": "WebSite", "name": SITE_NAME}])

    add(Page("", "Samuel T Sawian | Game Producer & Product Manager",
             "Portfolio of Samuel T Sawian, a game producer and product manager from Shillong. Bingo Bash, FarmVille 2, Teen Patti Gold, and product design for social impact.",
             "home", home_body, og_type="profile"),
        lambda pg: website(pg) + [person(), webpage_ld(pg, extra={"about": {"@type": "Person", "name": "Samuel T Sawian"}})])

    add(Page("games/", "Game Design Portfolio | Samuel T Sawian",
             "Games Samuel T Sawian has designed and produced: Bingo Bash, FarmVille 2, Teen Patti Gold, Dr Nero, Gameloft titles, Kitty Journey and more.",
             "games", games_body, crumbs=G, nav="games/"),
        lambda pg: [webpage_ld(pg, "CollectionPage")])

    game_meta = {
        "bingo-bash": ("Bingo Bash | Producer Case Study | Samuel T Sawian", "How Samuel T Sawian produced and designed features for Bingo Bash, the #1 free-to-play bingo game, through its growth to a $165M acquisition.", bingo_body,
                       game_ld("Bingo Bash", "Social casino", ["Facebook", "Android", "iOS"], [u for _, u in PLAY["bingo-bash"]], "The world's #1 free-to-play bingo game.")),
        "farmville-2": ("FarmVille 2 | Zynga | Samuel T Sawian", "Samuel T Sawian's work as Game Features and Content Producer on Zynga's FarmVille 2: 300,000 more daily players and a five-year vision.", farmville_body,
                        game_ld("FarmVille 2", "Simulation", ["Facebook"], [u for _, u in PLAY["farmville-2"]], "Zynga's farming simulation game, peaking at 40 million monthly active users.")),
        "teen-patti-gold": ("Teen Patti Gold | Moonfrog | Samuel T Sawian", "Samuel T Sawian's work as Game Producer on Teen Patti Gold, Moonfrog's top-grossing three-card game with more than 4M monthly players.", teenpatti_body,
                            game_ld("Teen Patti Gold", "Card game", ["Android", "iOS"], [u for _, u in PLAY["teen-patti-gold"]], "A top-grossing mobile three-card game from Moonfrog Labs.")),
        "dr-nero": ("Dr Nero | Serious Game Case Study | Samuel T Sawian", "A non-violent RPG that teaches research scientists to collaborate, designed by Samuel T Sawian for a Fortune 500 company. Gold Medal, LearnX Asia Pacific 2013.", nero_body,
                    game_ld("The Curious Case of Dr Nero", "Role-playing game", ["PC"], None, "An action-adventure RPG designed to promote collaboration among research scientists.")),
        "stellar-forever": ("Stellar Forever | Game Designer | Samuel T Sawian", "Stellar Forever, a 2D side-scrolling space brawler for PC and Xbox, designed and programmed by Samuel T Sawian at Vancouver Film School. Trailer and spotlight.", stellar_body,
                            game_ld("Stellar Forever", "Action-adventure", ["PC", "Xbox"], None, "A 2D side-scrolling action-adventure brawler set in outer space.")),
        "gameloft": ("Gameloft Titles | Game Producer | Samuel T Sawian", "Samuel T Sawian's work as Game Producer at Gameloft on mobile titles including Asphalt, Assassin's Creed, Spider-Man and James Cameron's Avatar.", gameloft_body,
                     None),
    }
    for slug, name in GAMES:
        title, desc, body, ld = game_meta[slug]
        add(Page(f"games/{slug}/", title, desc, slug, body, crumbs=G + [(name, f"games/{slug}/")], nav="games/", og_type="article"),
            (lambda ld: lambda pg: [webpage_ld(pg, extra={"about": ld} if ld else None)])(ld))

    add(Page("product/", "Product Design Portfolio | Samuel T Sawian",
             "Product work by Samuel T Sawian: Dentira, Recycled Earth, Meghalayan Age, and websites for Happy Feet School, Supercare and Bethany Hospitals.",
             "product", product_body, crumbs=P, nav="product/"),
        lambda pg: [webpage_ld(pg, "CollectionPage")])
    add(Page("product/recycled-earth/", "Recycled Earth | UX Case Study | Samuel T Sawian",
             "UX case study: an Android app that schedules and tracks waste collection for 22,000+ families in Maharashtra, run by Mumbai's ragpickers. Featured by UNICEF.",
             "recycled-earth", re_body, crumbs=P + [("Recycled Earth", "product/recycled-earth/")], nav="product/", og_type="article"),
        lambda pg: [webpage_ld(pg, extra={"about": creative_ld("Recycled Earth", "A mobile app to schedule and track household waste pickup and processing.", "SoftwareApplication") | {"operatingSystem": "Android", "applicationCategory": "UtilitiesApplication"}})])
    add(Page("product/meghalayan-age/", "Meghalayan Age | Branding & Packaging | Samuel T Sawian",
             "Brand identity, store and packaging design for Meghalayan Age, a Government of Meghalaya initiative: Lakadong turmeric premium range and 30+ food products.",
             "meghalayan-age", ma_body, crumbs=P + [("Meghalayan Age", "product/meghalayan-age/")], nav="product/", og_type="article"),
        lambda pg: [webpage_ld(pg, extra={"about": creative_ld("Meghalayan Age brand and packaging", "Brand identity and packaging for Meghalaya's indigenous food products.")})])

    add(Page("about/", "About Samuel T Sawian | Experience, Awards & Talks",
             "Experience at Dentira, Barking Deer Entertainment, NID, Zynga, GSN, Moonfrog, Tata Interactive and Gameloft, plus awards, education and talks.",
             "about", about_body, crumbs=HOME_C + [("About", "about/")], nav="about/", og_type="profile"),
        lambda pg: [webpage_ld(pg, "ProfilePage", {"mainEntity": person()})])

    add(Page("404.html", "Page not found | Samuel T Sawian", "This page doesn't exist.", "home", notfound_body, noindex=True),
        lambda pg: [])
    return pages

# ------------------------------------------------------------------ write
def main():
    css = ("/* Generated from _src/base.css + _src/extra.css. Edit those, then run _src/build.py. */\n" +
           FONTS + open(os.path.join(SRC, "base.css")).read() + open(os.path.join(SRC, "extra.css")).read())
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    open(os.path.join(OUT, "assets", "site.css"), "w").write(css)
    shutil.copy(os.path.join(SRC, "base.js"), os.path.join(OUT, "assets", "site.js"))
    if OUT != ROOT:
        for d in ("assets/img", "assets/og", "assets/fonts"):
            shutil.copytree(os.path.join(ROOT, d), os.path.join(OUT, d), dirs_exist_ok=True)
        for f in ("assets/favicon.svg", "assets/apple-touch-icon.png", "assets/icon-192.png", "assets/icon-512.png", "favicon.ico"):
            shutil.copy(os.path.join(ROOT, f), os.path.join(OUT, f))

    pages = build_pages()
    for pg in pages:
        out = os.path.join(OUT, pg.out)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w").write(render(pg))

    manifest = {"name": SITE_NAME, "short_name": "S.T.S", "start_url": "./", "display": "browser",
                "background_color": "#131615", "theme_color": "#131615",
                "icons": [{"src": "assets/icon-192.png", "sizes": "192x192", "type": "image/png"},
                          {"src": "assets/icon-512.png", "sizes": "512x512", "type": "image/png"}]}
    json.dump(manifest, open(os.path.join(OUT, "site.webmanifest"), "w"), indent=2)

    robots = "User-agent: *\nAllow: /\n"
    if SITE_URL:
        robots += f"\nSitemap: {SITE_URL}/sitemap.xml\n"
        urls = "".join(f"  <url><loc>{pg.abs()}</loc><lastmod>{TODAY}</lastmod></url>\n" for pg in pages if not pg.noindex)
        open(os.path.join(OUT, "sitemap.xml"), "w").write(
            f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    elif os.path.exists(os.path.join(OUT, "sitemap.xml")):
        os.remove(os.path.join(OUT, "sitemap.xml"))
    open(os.path.join(OUT, "robots.txt"), "w").write(robots)
    open(os.path.join(OUT, ".nojekyll"), "w").write("")
    print(f"Built {len(pages)} pages." + ("" if SITE_URL else "  SITE_URL is empty: canonical links and sitemap.xml were skipped."))

FONTS = """@font-face{font-family:"Bricolage Grotesque";src:url(fonts/bricolage-grotesque-latin-wght-normal.woff2) format("woff2");font-weight:200 800;font-style:normal;font-display:swap}
@font-face{font-family:"Instrument Sans";src:url(fonts/instrument-sans-latin-400-normal.woff2) format("woff2");font-weight:400;font-style:normal;font-display:swap}
@font-face{font-family:"Instrument Sans";src:url(fonts/instrument-sans-latin-500-normal.woff2) format("woff2");font-weight:500;font-style:normal;font-display:swap}
@font-face{font-family:"Instrument Sans";src:url(fonts/instrument-sans-latin-600-normal.woff2) format("woff2");font-weight:600;font-style:normal;font-display:swap}
@font-face{font-family:"IBM Plex Mono";src:url(fonts/ibm-plex-mono-latin-400-normal.woff2) format("woff2");font-weight:400;font-style:normal;font-display:swap}
@font-face{font-family:"IBM Plex Mono";src:url(fonts/ibm-plex-mono-latin-500-normal.woff2) format("woff2");font-weight:500;font-style:normal;font-display:swap}
.visually-hidden{position:absolute!important;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.h3like{font-size:var(--fs-l);letter-spacing:-.025em}
"""

if __name__ == "__main__":
    main()
