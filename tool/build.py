"""Builds the public HARU pages from the policy texts kept in the app's
repository (docs/public-release/privacy/*.md). Run: python3 tool/build.py"""
from pathlib import Path
import html
import json
import re

SITE = Path(__file__).resolve().parents[1]
# The app's repository sits beside this one.
SOURCE = SITE.parent / 'haru' / 'docs' / 'public-release' / 'privacy'
UPDATED = {
    'en': 'Last updated 18 November 2026',
    'fr': 'Mise à jour le 18 novembre 2026',
    'ko': '2026년 11월 18일 업데이트',
}
# The other languages say it as the app does (privacyUpdated in its ARB files).
ARB = SITE.parent / 'haru' / 'lib' / 'l10n'
LANGS = [
    ('en', 'English', 'index.html'), ('fr', 'Français', 'fr.html'), ('ko', '한국어', 'ko.html'),
    ('es', 'Español', 'es.html'), ('ja', '日本語', 'ja.html'), ('de', 'Deutsch', 'de.html'),
    ('it', 'Italiano', 'it.html'), ('pt', 'Português', 'pt.html'),
    ('zh-Hans', '简体中文', 'zh-hans.html'), ('zh-Hant', '繁體中文', 'zh-hant.html'),
    ('nl', 'Nederlands', 'nl.html'), ('pl', 'Polski', 'pl.html'), ('tr', 'Türkçe', 'tr.html'),
    ('id', 'Bahasa Indonesia', 'id.html'), ('vi', 'Tiếng Việt', 'vi.html'), ('th', 'ไทย', 'th.html'),
]
for code, _, _ in LANGS:
    if code not in UPDATED:
        UPDATED[code] = json.loads((ARB / f"intl_{code.replace('-', '_')}.arb").read_text())['privacyUpdated']
# The home, support and source pages' words, one file per language.
TEXT = {code: json.loads((SITE / 'tool' / 'pages' / f'{code}.json').read_text()) for code, _, _ in LANGS}
FILE = {code: href for code, _, href in LANGS}
# Scripts written without spaces between words: wrapped lines join as they are.
UNSPACED = {'ja', 'zh-Hans', 'zh-Hant', 'th'}
CONTACT = 'contact@super-dev.app'

STYLE = '''
@font-face { font-family: Haru; src: url("{root}assets/HaruPrototype-Regular.woff2") format("woff2"); font-weight: 400; font-display: swap; }
@font-face { font-family: Haru; src: url("{root}assets/HaruPrototype-Bold.woff2") format("woff2"); font-weight: 700; font-display: swap; }
/* Layout: one cream sheet under a sky band, like the app's screens. */
:root {
  --sky: #e8f3ff; --sheet: #fffdf6; --ink: #243a6b; --soft: #5f6f8f;
  --chip: rgba(36,58,107,.08); --line: rgba(36,58,107,.14); --button: #9cc9ff; --button-ink: #1b2a41;
  --display: Haru, "Apple SD Gothic Neo", "Noto Sans KR", system-ui, sans-serif;
  --text: system-ui, -apple-system, "Segoe UI", Roboto, "Apple SD Gothic Neo", "Noto Sans KR", sans-serif;
}
@media (prefers-color-scheme: dark) { :root {
  --sky: #16213f; --sheet: #1d2c52; --ink: #f4f1e6; --soft: #b7c2dc;
  --chip: rgba(255,253,246,.08); --line: rgba(255,253,246,.16); --button: #9cc9ff; --button-ink: #1b2a41;
  color-scheme: dark;
} }
* { box-sizing: border-box; }
body { margin: 0; background: var(--sky); color: var(--ink); font: 400 17px/1.55 var(--text); }
a { color: inherit; }
a:focus-visible { outline: 3px solid var(--button); outline-offset: 2px; border-radius: 6px; }
.wrap { max-width: 680px; margin: 0 auto; padding-inline: max(16px, env(safe-area-inset-left, 0px)) max(16px, env(safe-area-inset-right, 0px)); }
header.top { padding-block: 20px 8px; display: flex; flex-wrap: wrap; align-items: center; gap: 12px; }
header.top > * { min-width: 0; }
.mark { width: 44px; height: 44px; border-radius: 22px; background: var(--button); color: var(--button-ink); display: grid; place-items: center; font: 700 20px/1 "Apple SD Gothic Neo", "Noto Sans KR", sans-serif; text-decoration: none; flex: none; }
.brand { font: 700 18px/1.3 var(--display); text-decoration: none; }
.brand small { display: block; font-weight: 400; font-size: 13px; color: var(--soft); white-space: nowrap; }
nav.langs { margin-left: auto; display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; }
nav.langs a { font-size: 14px; padding: 6px 12px; border-radius: 16px; background: var(--chip); text-decoration: none; }
nav.langs a[aria-current="page"] { background: var(--button); color: var(--button-ink); font-weight: 700; }
main.sheet { background: var(--sheet); border-radius: 28px; padding: 28px 24px 32px; margin-block: 12px 40px; box-shadow: 0 4px 18px rgba(16,26,50,.12); }
h1 { font: 700 34px/1.15 var(--display); margin: 0 0 6px; text-wrap: balance; overflow-wrap: anywhere; }
.updated { color: var(--soft); font-size: 14px; margin: 0 0 20px; }
h2 { font-size: 13px; letter-spacing: .06em; text-transform: uppercase; color: var(--soft); margin: 28px 0 6px; }
p { margin: 0 0 12px; max-width: 65ch; overflow-wrap: anywhere; }
.hero { display: flex; align-items: flex-end; justify-content: space-between; gap: 12px; }
.hero img { width: 104px; height: auto; flex: none; }
.links { display: grid; gap: 10px; margin-top: 20px; }
.tile { display: flex; align-items: center; gap: 12px; padding: 14px 16px; border-radius: 18px; background: var(--chip); text-decoration: none; }
.tile strong { display: block; font: 700 17px/1.3 var(--display); }
.tile span { color: var(--soft); font-size: 14px; }
/* Long hashes and file names wrap inside their tile on a phone. */
.tile > span { min-width: 0; flex: 1; }
.tile strong, .tile span { overflow-wrap: anywhere; }
.tile::after { content: "›"; margin-left: auto; font-size: 22px; color: var(--soft); }
.mail { display: inline-block; font-weight: 700; user-select: all; padding: 8px 14px; border-radius: 14px; background: var(--chip); }
:lang(ko) p, :lang(ko) h1 { word-break: keep-all; }
:lang(th) p, :lang(ja) p, :lang(zh) p { line-break: strict; }
footer { color: var(--soft); font-size: 13px; padding-block: 0 32px; text-align: center; }
@media (max-width: 480px) { h1 { font-size: 28px; } main.sheet { padding: 22px 18px 26px; } .hero img { width: 80px; } nav.langs { margin-left: 0; width: 100%; justify-content: flex-start; } }
'''


def page(lang, title, body, root, langs=None):
    t, own = TEXT[lang], FILE[lang]
    switch = ''
    if langs:
        switch = '<nav class="langs" aria-label="Language">' + ''.join(
            f'<a href="{href}" hreflang="{code}" lang="{code}"' + (' aria-current="page"' if code == lang else '') + f'>{name}</a>'
            for code, name, href in langs) + '</nav>'
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="HARU 하루 — {html.escape(t['slogan'])}">
<style>{STYLE.replace('{root}', root)}</style>
</head>
<body>
<div class="wrap">
<header class="top">
<a class="mark" href="{root}{own}" aria-label="HARU">하</a>
<a class="brand" href="{root}{own}">HARU 하루<small>{html.escape(t['slogan'])}</small></a>
{switch}
</header>
<main class="sheet">
{body}
</main>
<footer>HARU · Super-dev · SDT Consulting · <a href="{root}privacy/{own}">{html.escape(t['footerPrivacy'])}</a> · <a href="{root}support/{own}">{html.escape(t['footerSupport'])}</a></footer>
</div>
</body>
</html>
'''


def policy(lang):
    text = (SOURCE / f'{lang}.md').read_text()
    lines = text.splitlines()
    title = lines[0].removeprefix('# ').strip()
    # The draft's own warning line goes; the page shows its date instead.
    blocks = re.split(r'\n\s*\n', '\n'.join(lines[1:]).strip())
    # The first block is the draft's warning line, in every language.
    blocks = blocks[1:] if not blocks[0].startswith('## ') else blocks
    out = [f'<h1>{html.escape(title)}</h1>', f'<p class="updated">{UPDATED[lang]}</p>']
    for block in blocks:
        block = block.strip()
        if not block or re.search(r'review before publication|à relire avant publication|공개 전 검토', block):
            continue
        if block.startswith('## '):
            out.append(f'<h2>{html.escape(block[3:].strip())}</h2>')
            continue
        joined = ('' if lang in UNSPACED else ' ').join(l.strip() for l in block.splitlines())
        escaped = html.escape(joined).replace(html.escape(CONTACT), f'<a href="mailto:{CONTACT}">{CONTACT}</a>')
        out.append(f'<p>{escaped}</p>')
    return title, '\n'.join(out)


for code, name, href in LANGS:
    title, body = policy(code)
    langs = [(c, n, h) for c, n, h in LANGS]
    (SITE / 'privacy' / href).write_text(page(code, title, body, '../', langs))

for code, _, href in LANGS:
    t = TEXT[code]
    e = {k: html.escape(v) for k, v in t.items()}
    home = f'''<div class="hero"><div>
<h1>HARU 하루</h1>
<p class="updated">{e['slogan']}</p>
</div><img src="assets/cat.webp" alt="{e['catAlt']}" width="104" height="104"></div>
<p>{e['homeIntro']}</p>
<div class="links">
<a class="tile" href="privacy/{href}"><span><strong>{e['privacyTile']}</strong><span>{e['privacyTileHint']}</span></span></a>
<a class="tile" href="support/{href}"><span><strong>{e['supportTile']}</strong><span>{e['supportTileHint']}</span></span></a>
<a class="tile" href="sources/{href}"><span><strong>{e['sourcesTile']}</strong><span>{e['sourcesTileHint']}</span></span></a>
</div>'''
    (SITE / href).write_text(page(code, 'HARU 하루', home, '', LANGS))

    support = f'''<h1>{e['supportTitle']}</h1>
<p class="updated">HARU · Super-dev</p>
<p>{e['supportIntro']}</p>
<p><span class="mail">{CONTACT}</span></p>
<h2>{e['supportDataTitle']}</h2>
<p>{e['supportDataBody']}</p>'''
    (SITE / 'support' / href).write_text(page(code, f"{t['supportTitle']} · HARU", support, '../', LANGS))

# The source code HARU's FFmpeg libraries are built from (LGPL 3.0). The
# archives sit beside the page; SHA256SUMS lists their fingerprints.
ARCHIVES = [
    ('ffmpeg-8.1.2.tar.xz', 'FFmpeg 8.1.2, the official release (tag n8.1.2), not modified'),
    ('ffmpeg-8.1.2.tar.xz.asc', 'Its signature by the FFmpeg release key FCF9 86EA 15E6 E293 A564 4F10 B432 2F04 D676 58D8'),
    ('ffmpeg-kit-android-apple-8.1.2.tar.gz', 'FFmpegKit at commit 984fa2dba93f93cd768dccb3033e6f175c46d3b5 (tag android-apple-8.1.2 of github.com/sk3llo/ffmpeg-kit): the ffmpegkit library and the scripts that configured and built FFmpeg'),
    ('cpu_features-0.8.0.tar.gz', 'cpu_features 0.8.0 (Google, Apache 2.0), used by FFmpegKit on Android'),
    ('LGPL-3.0.txt', 'GNU Lesser General Public License 3.0'),
    ('GPL-3.0.txt', 'GNU General Public License 3.0'),
    ('Apache-2.0-cpu_features.txt', 'Licence of cpu_features'),
    ('SHA256SUMS', 'SHA-256 of every file above'),
]


def size(name):
    n = (SITE / 'sources' / name).stat().st_size
    return f'{n / 1e6:.1f} MB' if n >= 1e5 else f'{max(1, round(n / 1e3))} kB'


files = '\n'.join(
    f'<a class="tile" href="{html.escape(name)}"><span><strong>{html.escape(name)}</strong>'
    f'<span>{html.escape(what)} · {size(name)}</span></span></a>'
    for name, what in ARCHIVES)
for code, _, href in LANGS:
    t = TEXT[code]
    e = {k: html.escape(v) for k, v in t.items()}
    # These two keep their HTML (<code>, &lt;abi&gt;) as written in the texts.
    raw = {k: t[k] for k in ('sourcesBuildBody', 'sourcesUseBody')}
    offer = e['sourcesOfferBody'].replace('{mail}', f'<a href="mailto:{CONTACT}">{CONTACT}</a>')
    note = '' if code == 'en' else f"<p class=\"updated\">{e['sourcesLegalNote']}</p>\n"
    sources = f'''<h1>{e['sourcesTitle']}</h1>
<p class="updated">{e['sourcesUpdated']}</p>
{note}<p>{e['sourcesIntro']}</p>
<h2>{e['sourcesCarriesTitle']}</h2>
<p>{e['sourcesCarriesBody']}</p>
<p class="updated">{e['sourcesFilesNote']}</p>
<div class="links">
{files}
</div>
<h2>{e['sourcesBuildTitle']}</h2>
<p>{raw['sourcesBuildBody']}</p>
<h2>{e['sourcesUseTitle']}</h2>
<p>{raw['sourcesUseBody']}</p>
<h2>{e['sourcesOfferTitle']}</h2>
<p>{offer}</p>
<p>{e['sourcesTrademark']}</p>'''
    (SITE / 'sources' / href).write_text(page(code, f"{t['sourcesTitle']} · HARU", sources, '../', LANGS))
print('built')
