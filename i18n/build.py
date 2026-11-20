"""Build the French, Kiswahili and Brazilian Portuguese copies of MatchIQ under /fr/, /sw/ and /pt/.

Run after any change to the English pages: python3 i18n/build.py
Every visible text, label and dashboard script text is looked up by its exact English wording in
i18n/strings.py. A missing translation stops the build and is listed in i18n/missing.txt, so no
English is left on a translated page. Names, scores and the source titles stay as written."""
import json, re, sys, pathlib
from bs4 import BeautifulSoup, NavigableString
from bs4.element import PreformattedString

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "i18n"))
from strings import S, JS

BASE = "https://afritech-advisory.github.io/afritech-matchiq/"
HOME = "https://afritechsports.github.io/"
PAGES = ["index.html"] + sorted(str(p.relative_to(ROOT)) for p in (ROOT / "matches").glob("*/index.html"))
LANGS = [("en", "English", "en"), ("fr", "Français", "fr"), ("sw", "Kiswahili", "sw"), ("pt", "Português", "pt-BR")]
LABEL = {"en": "Language", "fr": "Langue", "sw": "Lugha", "pt": "Idioma"}
ATTRS = ("alt", "title", "aria-label", "placeholder")
LETTER = re.compile(r"[A-Za-z]{2}")
KEEP = {"Afritech Sports", "MatchIQ", "AFRITECH MATCHIQ™", "Stephen", "Umejiaku", "Anri Ito", "Fuki Ito", "39' Bashiru", "47' Umejiaku", "80' Fuki Ito",
        "39' Bashiru, 0–1", "47' Umejiaku, 0–2", "80' Fuki Ito, 1–2", "39' Bashiru · 47' Umejiaku · 80' Fuki Ito",
        "Afritech Sports Technology and Innovation Group Limited"}
SOURCE = re.compile(r"^[A-Z][\w .]+ \| .+ ›$")  # titles in the sources list stay as written
CSS = ('<style id="afs-lang-css">.afs-lang{background:#0B1C33;font:600 13px/1 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;'
       'text-align:center;padding:6px 8px}.afs-lang a{color:#C9D6E6;text-decoration:none;padding:6px 8px;border-radius:6px;display:inline-block}'
       '.afs-lang a.on{background:#14B8A6;color:#06221F}</style>')


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def names(html):
    """Player and coach names from the dashboard data: kept as written."""
    out = set()
    for m in re.finditer(r'"(?:a|b)": "([^"]+)"', html):
        out.add(m[1])
    return out


def switcher(rel, lang):
    links = "".join(f'<a href="{BASE + ("" if c == "en" else c + "/") + rel}" hreflang="{c}"{" class=on" if c == lang else ""}>{n}</a>' for c, n, _ in LANGS)
    return f'<!-- afs-lang:start -->{CSS}<nav class="afs-lang" aria-label="{LABEL[lang]}">{links}</nav><!-- afs-lang:end -->'


def add_switch(html, rel, lang):
    html = re.sub(r"<!-- afs-lang:start -->.*?<!-- afs-lang:end -->", "", html, flags=re.S)
    html = re.sub(r'<link rel="alternate" hreflang=[^>]*>', "", html)
    alt = "".join(f'<link rel="alternate" hreflang="{h}" href="{BASE + ("" if c == "en" else c + "/") + rel}">' for c, _, h in LANGS)
    html = html.replace("</head>", alt + "</head>", 1)
    i = html.find("<!-- afs-bar:end -->")
    i = i + len("<!-- afs-bar:end -->") if i >= 0 else html.index(">", html.index("<body")) + 1
    return html[:i] + switcher(rel, lang) + html[i:]


def translate(html, rel, lang, d, keep, missing):
    def tr(t):
        k = norm(t)
        if k in d:
            return d[k]
        if not LETTER.search(k) or k in keep or k in KEEP or SOURCE.match(k) or "@" in k:
            return t
        missing.add(k)
        return t
    soup = BeautifulSoup(html, "html.parser")
    for s in soup.find_all(string=True):
        if isinstance(s, PreformattedString) or s.parent.name in ("script", "style"):
            continue
        t = norm(s)
        if t and LETTER.search(t):
            lead, trail = s[: len(s) - len(s.lstrip())], s[len(s.rstrip()):]
            s.replace_with(NavigableString(lead + tr(t) + trail))
    for el in soup.find_all(True):
        for a in ATTRS:
            if el.has_attr(a):
                el[a] = tr(el[a])
        if el.name == "meta" and (el.get("name") == "description" or el.get("property", "").startswith("og:t") or el.get("property") == "og:description"):
            el["content"] = tr(el["content"])
        if el.name == "a" and el.get("href", "").startswith(HOME) and "lang=" not in el["href"]:
            el["href"] += ("&" if "?" in el["href"] else "?") + "lang=" + lang
    for sc in soup.find_all("script"):
        txt = sc.string or ""
        # dashboard data: translate the text values of GOALS and ROLES, keep ids, links and names
        for var in ("GOALS", "ROLES"):
            m = re.search(r"const " + var + r"=(\{.*?\});", txt, re.S)
            if not m:
                continue
            data = json.loads(m[1])
            def walk(o, key=None):
                if isinstance(o, dict):
                    return {k: walk(v, k) for k, v in o.items()}
                if isinstance(o, list):
                    return [walk(v, key) for v in o]
                if isinstance(o, str) and key in ("title", "body", "why", "note", "labels", "a", "b"):
                    return tr(o)
                return o
            txt = txt.replace(m[1], json.dumps(walk(data), ensure_ascii=False), 1)
        for en, t in JS.get(lang, {}).items():
            txt = txt.replace("'" + en + "'", "'" + t.replace("'", "\\'") + "'").replace(en if en.startswith("<th>") or en == " of " else "\0", t)
        if txt != (sc.string or ""):
            sc.string = txt
    out = str(soup)
    out = re.sub(r'<html lang="[^"]*"', f'<html lang="{dict((c, h) for c, _, h in LANGS)[lang]}"', out, count=1)
    # copies sit one folder deeper: relative links to assets go up one level
    out = re.sub(r'(src|href)="assets/', r'\1="../assets/', out)
    return out


def main():
    missing, made = set(), 0
    for i, (code, _, _) in enumerate(LANGS[1:], start=1):
        d = {e[0]: e[i] for e in S}
        JS[code] = {e[0]: e[i] for e in JS_LIST}
        for rel in PAGES:
            src = re.sub(r"<!-- afs-lang:start -->.*?<!-- afs-lang:end -->", "", (ROOT / rel).read_text(), flags=re.S)
            rel_url = "" if rel == "index.html" else rel[: -len("index.html")]
            keep = names(src)
            out = translate(src, rel_url, code, d, keep, missing)
            dest = ROOT / code / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(add_switch(out, rel_url, code))
            made += 1
    for rel in PAGES:  # the English pages get the language bar too
        p = ROOT / rel
        p.write_text(add_switch(p.read_text(), "" if rel == "index.html" else rel[: -len("index.html")], "en"))
    (ROOT / "i18n/missing.txt").write_text("\n".join(sorted(missing)))
    if missing:
        sys.exit(f"Missing translations: {len(missing)} (see i18n/missing.txt)")
    print(f"built {made} translated pages, no missing text")


JS_LIST = JS
JS = {}
if __name__ == "__main__":
    main()
