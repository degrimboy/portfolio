# Samuel T Sawian — portfolio site

A static, multi-page portfolio. Plain HTML, CSS and a little JavaScript. No framework, no build tools beyond Python 3.

```
index.html                     Home
games/                         Game design overview
games/bingo-bash/              One page per major game
games/farmville-2/
games/teen-patti-gold/
games/dr-nero/
games/gameloft/
product/                       Product design overview (also nULTA, 7 Sisters Kitchen)
product/recycled-earth/        Case studies
product/meghalayan-age/
about/                         Experience, awards, education, talks
404.html                       Not-found page (GitHub Pages uses it automatically)
assets/                        CSS, JS, fonts, images, social-share images, icons
_src/                          The source: edit here, then rebuild
robots.txt, site.webmanifest, favicon.ico, .nojekyll
sitemap.xml                    Created once SITE_URL is set
```

## 1. Put it on GitHub Pages

1. Create a new GitHub repository, for example `portfolio`. Public repos get Pages for free.
2. Upload **everything in this folder**, including `_src/` and the hidden `.nojekyll` file, to the `main` branch.
3. In the repo, open **Settings → Pages**. Under *Build and deployment*, choose **Deploy from a branch**, branch **main**, folder **/ (root)**, and save.
4. After a minute the site is live at `https://<your-username>.github.io/portfolio/`.

## 2. Set the site address (important for SEO)

Open `_src/build.py` and set the `SITE_URL` line near the top:

```python
SITE_URL = "https://<your-username>.github.io/portfolio"   # no trailing slash
```

Then rebuild and push:

```bash
python3 _src/build.py
git add -A && git commit -m "Set site URL" && git push
```

This adds canonical links, full social-share image URLs, structured-data URLs and `sitemap.xml`. All four need the full address, so the build leaves them out until `SITE_URL` is set.

## 3. Tell Google and Bing about it

* **Google Search Console** (search.google.com/search-console): add the site, verify it, then submit `sitemap.xml` under *Sitemaps*.
* **Bing Webmaster Tools** (bing.com/webmasters): sign in and import the site straight from Search Console.
* Check the structured data with Google's **Rich Results Test** and social cards with LinkedIn's **Post Inspector**.

## 4. Moving to your own domain later

1. In **Settings → Pages → Custom domain**, enter the domain (for example `www.samuelsawian.com`). GitHub adds a `CNAME` file to the repo.
2. At your domain registrar, add the DNS records GitHub shows you (a `CNAME` record for `www`, and `A` records for the bare domain).
3. Tick **Enforce HTTPS** once it becomes available.
4. Change `SITE_URL` in `_src/build.py` to the new domain, run `python3 _src/build.py`, and push.
5. In Search Console, add the new domain and use *Change of address* so rankings carry over.

## Editing content

All page text lives in `_src/build.py`, one function per page (`home_body`, `bingo_body`, `about_body` and so on). Page titles and descriptions for search results are set in `build_pages()` near the bottom.

* Styles: `_src/base.css` and `_src/extra.css`
* Script (wave animation, image viewer): `_src/base.js`
* New images: add a `.webp` to `assets/img/`, then add its width and height to `_src/image-sizes.json`. For images wider than 900px, also add a `name-800.webp` copy for phones.

Always run `python3 _src/build.py` after editing. It rewrites the HTML files, `assets/site.css`, `assets/site.js`, `robots.txt` and the sitemap.

## Standards it follows

* **Accessibility (WCAG 2.2 AA):** semantic landmarks, one `h1` per page, ordered headings, skip link, visible keyboard focus, alt text on every image, breadcrumbs, `aria-current` in the navigation, reduced-motion support, sufficient colour contrast, 40px+ tap targets.
* **Core Web Vitals:** self-hosted fonts with `font-display: swap` and preloading, width and height on every image (no layout shift), lazy loading below the fold, a high-priority hero image, responsive `srcset` images in WebP, about 2KB of deferred JavaScript.
* **SEO:** a unique title and description per page, canonical URLs, Open Graph and Twitter cards with a 1200×630 image per page, JSON-LD structured data (`Person`, `WebSite`, `ProfilePage`, `VideoGame`, `BreadcrumbList`), `sitemap.xml`, `robots.txt`, descriptive URLs, `lang="en-IN"`.

Lighthouse (mobile and desktop) scored 100 for Accessibility, Best Practices and SEO, and 95 to 100 for Performance, on the pages tested.
