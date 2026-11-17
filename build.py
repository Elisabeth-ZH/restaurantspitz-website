#!/usr/bin/env python3
"""Erzeugt alle Seiten von restaurantspitz.ch (DE und EN) als statisches HTML.

Aufruf:  python3 build.py
Inhalte stehen unten in den Abschnitten DE/EN. Bilder liegen in bilder/ als
AVIF und WebP (je Breite eine Datei, Name: <bild>-<breite>.<format>).
"""
import html, json, os, re
from PIL import Image

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://restaurantspitz.ch'
ALENO = {
    'de': 'https://mytools.aleno.me/reservations/v2.0/reservations.html?k=eyJrIjoid2l2dTVrM2lsNm15cnBiOWlwdzZ4bmViajhycnVkaWRpZ280bGZwODBsbzlhNGlweTEiLCJsIjoiZGUiLCJyIjoibVlTbXdSSlpmTTR6Z2UzTXQiLCJzIjoiaHR0cHM6Ly9teXRvb2xzLmFsZW5vLm1lLyJ9',
    'en': 'https://mytools.aleno.me/reservations/v2.0/reservations.html?k=eyJrIjoid2l2dTVrM2lsNm15cnBiOWlwdzZ4bmViajhycnVkaWRpZ280bGZwODBsbzlhNGlweTEiLCJsIjoiZW4iLCJyIjoibVlTbXdSSlpmTTR6Z2UzTXQiLCJzIjoiaHR0cHM6Ly9teXRvb2xzLmFsZW5vLm1lLyJ9',
}
WEB3FORMS_KEY = '18d92e32-ee57-41a1-9c5f-d81095375a6b'  # vorläufig: geht an elisabeth@restaurantspitz.ch
GTM = 'GTM-T3V5B8LB'
e = html.escape

# ---------------------------------------------------------------- Bilder
_bilder = {}
for f in os.listdir(os.path.join(ROOT, 'bilder')):
    m = re.match(r'(.+)-(\d+)\.webp$', f)
    if m:
        _bilder.setdefault(m.group(1), []).append(int(m.group(2)))

def bild(name, alt, sizes='100vw', lazy=True, cls=''):
    breiten = sorted(_bilder[name])
    w = breiten[-1]
    with Image.open(os.path.join(ROOT, 'bilder', f'{name}-{w}.webp')) as im:
        bw, bh = im.size
    src = lambda fmt: ', '.join(f'/bilder/{name}-{b}.{fmt} {b}w' for b in breiten)
    laden = 'loading="lazy" decoding="async"' if lazy else 'fetchpriority="high"'
    k = f' class="{cls}"' if cls else ''
    return (f'<picture{k}><source type="image/avif" srcset="{src("avif")}" sizes="{sizes}">'
            f'<source type="image/webp" srcset="{src("webp")}" sizes="{sizes}">'
            f'<img src="/bilder/{name}-{breiten[0]}.webp" width="{bw}" height="{bh}" alt="{e(alt)}" {laden}></picture>')

def karussell(namen, alt, sizes, auto=False, hell=False, cls='', erstes_eager=False):
    teile = []
    for i, n in enumerate(namen):
        teile.append(f'<div class="bild">{bild(n, alt if i == 0 else "", sizes, lazy=not (erstes_eager and i == 0))}</div>')
    attr = ' data-auto' if auto else ''
    klassen = ' '.join(x for x in ['karussell', 'hell' if hell else '', cls] if x)
    return f'<div class="{klassen}"{attr}><div class="spur" tabindex="0" aria-label="{e(alt)}">{"".join(teile)}</div></div>'

def pfeilliste(links, cls='pfeilliste'):
    li = ''.join(f'<li><a href="{u}"{" target=_blank rel=noopener" if u.startswith("http") or u.endswith(".pdf") else ""}>{e(t)}</a></li>' for t, u in links)
    return f'<ul class="{cls}">{li}</ul>'

# ---------------------------------------------------------------- Texte
T = {
 'de': {
  'nav': [('Event buchen', '/event'), ('Gutschein', '/gutscheine'), ('Newsletter', '/newsletter'), ('Kontakt', '/kontakt')],
  'anker': [('Restaurant', 'restaurant'), ('Terrasse', 'terrasse'), ('Bar', 'bar'), ('Bistro', 'bistro'), ('Anlässe', 'anlass'),
            ('Öffnungszeiten', 'oeffnungszeiten'), ('Jobs', 'jobs'), ('Friends', 'friends')],
  'home': '/', 'andere': ('E', 'English', 'en'), 'menue': 'Menü', 'skip': 'Zum Inhalt springen',
  'reservieren': 'Tisch<br> im Restaurant<br> reservieren',
  'fuss_name': 'Spitz, Restaurant / Bar / Bistro / Anlässe', 'tel': 'Telefon', 'email': 'E-Mail',
  'impressum': ('Impressum', '/impressum'), 'datenschutz': ('Datenschutzerklärung', '/datenschutz'), 'agb': ('AGB', '/agb'),
  'fuss_links': 'Links', 'fuss_folgen': 'Folgen Sie uns', 'fuss_kontakt': 'Kontakt',
 },
 'en': {
  'nav': [('Events', '/en/events'), ('Vouchers', '/en/vouchers'), ('Newsletter', '/en/newsletter'), ('Contact', '/en/contact')],
  'anker': [('Restaurant', 'restaurant'), ('Terrace', 'terrasse'), ('Bar', 'bar'), ('Bistro', 'bistro'), ('Events', 'anlass'),
            ('Opening hours', 'oeffnungszeiten'), ('Jobs', 'jobs'), ('Friends', 'friends')],
  'home': '/en/', 'andere': ('D', 'Deutsch', 'de'), 'menue': 'Menu', 'skip': 'Skip to content',
  'reservieren': 'Book<br> a table<br> now',
  'fuss_name': 'Spitz, Restaurant / Bar / Bistro / Events', 'tel': 'Phone', 'email': 'Email',
  'impressum': ('Imprint', '/en/impressum'), 'datenschutz': ('Privacy policy', '/en/privacy'), 'agb': ('Terms', '/en/agb'),
  'fuss_links': 'Links', 'fuss_folgen': 'Follow us', 'fuss_kontakt': 'Contact',
 },
}

# Seitenpaare DE <-> EN (für Sprachumschalter und hreflang)
PAARE = [('/', '/en/'), ('/event', '/en/events'), ('/gutscheine', '/en/vouchers'), ('/newsletter', '/en/newsletter'),
         ('/kontakt', '/en/contact'), ('/impressum', '/en/impressum'), ('/agb', '/en/agb'), ('/datenschutz', '/en/privacy'),
         ('/gutscheinbestellung', '/en/voucher-order'), ('/danke', '/en/thanks')]
def gegenstueck(pfad, lang):
    for de, en in PAARE:
        if lang == 'de' and pfad == de: return en
        if lang == 'en' and pfad == en: return de
    return T['de' if lang == 'en' else 'en']['home']

HERZ = '<svg class="herz" viewBox="0 0 100 90" aria-hidden="true"><path fill="#f0c6ef" d="M50 88C20 64 2 47 2 27 2 12 13 2 27 2c10 0 18 6 23 14C55 8 63 2 73 2c14 0 25 10 25 25 0 20-18 37-48 61z"/></svg>'

def seite(lang, pfad, titel, beschreibung, inhalt, aktiv=None, ldjson=None):
    t = T[lang]
    nav = ''.join(f'<a href="{u}"{" aria-current=page" if u == aktiv else ""}>{e(n)}</a>' for n, u in t['nav'])
    home = t['home']
    anker = ''.join(f'<li><a href="{home}#{a}">{e(n)}</a></li>' for n, a in t['anker'])
    klein = ''.join(f'<li><a href="{u}">{e(n)}</a></li>' for n, u in t['nav'])
    kurz, lang_name, lang_code = t['andere']
    anderer = gegenstueck(pfad, lang)
    de_url, en_url = (pfad, anderer) if lang == 'de' else (anderer, pfad)
    tel_anzeige = '044 221 94 77'
    ld = f'<script type="application/ld+json">{json.dumps(ldjson, ensure_ascii=False)}</script>' if ldjson else ''
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titel)}</title>
<meta name="description" content="{e(beschreibung)}">
<link rel="canonical" href="{SITE}{pfad}">
<link rel="alternate" hreflang="de" href="{SITE}{de_url}">
<link rel="alternate" hreflang="en" href="{SITE}{en_url}">
<link rel="alternate" hreflang="x-default" href="{SITE}{de_url}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(titel)}">
<meta property="og:description" content="{e(beschreibung)}">
<meta property="og:url" content="{SITE}{pfad}">
<meta property="og:image" content="{SITE}/bilder/main-14-1600.webp">
<link rel="icon" href="/favicon/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon/favicon-96x96.png" sizes="96x96" type="image/png">
<link rel="apple-touch-icon" href="/favicon/apple-touch-icon.png">
<link rel="preload" href="/schriften/Gilroy-Bold.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/schriften/Sabon-LTPro-Roman.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/site.css">
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})(window,document,'script','dataLayer','{GTM}');</script>
{ld}
</head>
<body>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={GTM}" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<a class="skip" href="#inhalt">{t['skip']}</a>
<header class="kopf">
  <a class="logo" href="{home}" aria-label="Restaurant Spitz"><img src="/bilder/logo-spitz.svg" alt="Spitz" width="150" height="150"></a>
  <nav class="hauptnav" aria-label="Hauptnavigation">{nav}</nav>
  <a class="sprache" href="{anderer}" hreflang="{lang_code}" lang="{lang_code}" aria-label="{lang_name}">{kurz}</a>
  <button class="menueknopf" type="button" aria-expanded="false" aria-controls="menue" aria-label="{t['menue']}"><span></span><span></span><span></span></button>
</header>
<div class="menue" id="menue">
  <ul class="gross">{anker}</ul>
  <ul class="klein">{klein}</ul>
</div>
<a class="reservieren" href="{ALENO[lang]}" target="_blank" rel="noopener">{t['reservieren']}<span class="pfeil" aria-hidden="true"></span></a>
<main id="inhalt">
{inhalt}
</main>
<footer class="fuss">
  <div class="fuss-raster">
    <div>
      <h2>{t['fuss_kontakt']}</h2>
      <p>{t['fuss_name']}<br>Museumstrasse 2, 8001 Zürich<br>
      {t['tel']}: <a href="tel:+41442219477">{tel_anzeige}</a><br>
      {t['email']}: <a href="mailto:info@restaurantspitz.ch">info@restaurantspitz.ch</a></p>
    </div>
    <div>
      <h2>{t['fuss_links']}</h2>
      <ul>{''.join(f'<li><a href="{u}">{e(n)}</a></li>' for n, u in [t['impressum'], t['datenschutz'], t['agb']])}</ul>
    </div>
    <div>
      <h2>{t['fuss_folgen']}</h2>
      <div class="sozial">
        <a href="https://www.facebook.com/RestaurantBarBistroSpitz/" target="_blank" rel="noopener" aria-label="Facebook"><img src="/bilder/facebook.png" alt="" width="32" height="32"></a>
        <a href="https://www.instagram.com/restaurantspitz/" target="_blank" rel="noopener" aria-label="Instagram"><img src="/bilder/instagram.png" alt="" width="32" height="32"></a>
        <a href="https://www.tripadvisor.ch/Restaurant_Review-g188113-d10696560-Reviews-Spitz-Zurich.html" target="_blank" rel="noopener" aria-label="Tripadvisor"><img src="/bilder/trip.png" alt="" width="32" height="32"></a>
      </div>
    </div>
  </div>
</footer>
<script src="/site.js" defer></script>
</body>
</html>
'''

# ---------------------------------------------------------------- Öffnungszeiten (Daten für Anzeige und JSON-LD)
ZEITEN = {
 'de': [('Restaurant', [('Mo – Fr', '11.30 – 14.00 Uhr<br>18.00 – 23.00 Uhr'), ('Sa', '18.00 – 23.00 Uhr'), ('So', 'Geschlossen')]),
        ('Bar', [('Mo', 'Geschlossen'), ('Di – Sa', '17.00 – 23.00 Uhr'), ('So', 'Geschlossen')]),
        ('Bistro', [('Mo', 'Geschlossen'), ('Di – So', '10.00 – 17.00 Uhr')])],
 'en': [('Restaurant', [('Mon – Fri', '11.30 am – 2 pm<br>6 pm – 11 pm'), ('Sat', '6 pm – 11 pm'), ('Sun', 'Closed')]),
        ('Bar', [('Mon', 'Closed'), ('Tue – Sat', '5 pm – 11 pm'), ('Sun', 'Closed')]),
        ('Bistro', [('Mon', 'Closed'), ('Tue – Sun', '10 am – 5 pm')])],
}
BESONDERE = {
 'de': ['Mittwoch, 23.12.2026: Restaurant & Bar offen, Bistro 10.00 – 17.00',
        'Donnerstag, 24.12.2026, Heiligabend: Restaurant & Bar geschlossen, Bistro 10.00 – 14.00',
        'Freitag, 25.12.2026, Weihnachten: Restaurant & Bar geschlossen, Bistro 10.00 – 17.00',
        'Samstag, 26.12.2026, Stephanstag: Restaurant & Bar geschlossen, Bistro 10.00 – 17.00',
        'Sonntag, 27.12. bis Mittwoch, 30.12.2026: Restaurant & Bar geschlossen, Bistro 10.00 – 17.00',
        'Donnerstag, 31.12.2026, Silvester: Restaurant & Bar offen, Bistro 10.00 – 17.00',
        'Freitag, 01.01.2027, Neujahr: Restaurant & Bar geschlossen, Bistro 10.00 – 17.00',
        'Samstag, 02.01.2027, Berchtoldstag: Restaurant & Bar geschlossen, Bistro 10.00 – 17.00',
        'Sonntag, 03.01.2027: Restaurant & Bar geschlossen, Bistro 10.00 – 17.00',
        'Montag, 04.01.2027: Restaurant & Bar geschlossen, Bistro 10.00 – 17.00',
        'Dienstag, 05.01.2027: Restaurant & Bar offen, Bistro geschlossen'],
 'en': ['Wednesday, 23 December 2026: Restaurant & Bar open, Bistro 10 am – 5 pm',
        'Thursday, 24 December 2026, Christmas Eve: Restaurant & Bar closed, Bistro 10 am – 2 pm',
        'Friday, 25 December 2026, Christmas Day: Restaurant & Bar closed, Bistro 10 am – 5 pm',
        'Saturday, 26 December 2026, St. Stephen’s Day: Restaurant & Bar closed, Bistro 10 am – 5 pm',
        'Sunday, 27 December to Wednesday, 30 December 2026: Restaurant & Bar closed, Bistro 10 am – 5 pm',
        'Thursday, 31 December 2026, New Year’s Eve: Restaurant & Bar open, Bistro 10 am – 5 pm',
        'Friday, 1 January 2027, New Year’s Day: Restaurant & Bar closed, Bistro 10 am – 5 pm',
        'Saturday, 2 January 2027, Berchtold’s Day: Restaurant & Bar closed, Bistro 10 am – 5 pm',
        'Sunday, 3 January 2027: Restaurant & Bar closed, Bistro 10 am – 5 pm',
        'Monday, 4 January 2027: Restaurant & Bar closed, Bistro 10 am – 5 pm',
        'Tuesday, 5 January 2027: Restaurant & Bar open, Bistro closed'],
}
LD_RESTAURANT = {
 '@context': 'https://schema.org', '@type': 'Restaurant', 'name': 'Restaurant Spitz', 'url': SITE + '/',
 'telephone': '+41 44 221 94 77', 'email': 'info@restaurantspitz.ch', 'image': SITE + '/bilder/main-14-1600.webp',
 'address': {'@type': 'PostalAddress', 'streetAddress': 'Museumstrasse 2', 'postalCode': '8001', 'addressLocality': 'Zürich', 'addressCountry': 'CH'},
 'acceptsReservations': 'True', 'menu': SITE + '/files/Abendkarte_Herbst-Winter_HP-Final2026.pdf',
 'openingHoursSpecification': [
   {'@type': 'OpeningHoursSpecification', 'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], 'opens': '11:30', 'closes': '14:00'},
   {'@type': 'OpeningHoursSpecification', 'dayOfWeek': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'], 'opens': '18:00', 'closes': '23:00'}],
 'sameAs': ['https://www.instagram.com/restaurantspitz/', 'https://www.facebook.com/RestaurantBarBistroSpitz/'],
}

FRIENDS = [
 ('Greulich', 'https://greulich.ch/', 'Das Design Hotel im Kreis 4 in Zürich gehört zur Familie. Die Betreiber des Spitz heissen Sie dort in ihrem Hotel herzlich willkommen und sorgen für einen tollen Aufenthalt.',
  'The design hotel in District 4 in Zurich is part of the family. The operators of Spitz warmly welcome you to their hotel and ensure a wonderful stay.'),
 ('555+', 'https://www.555thai.ch/', 'Zum Hotel Greulich gehört das legendäre Thai Food Restaurant 555+. Hier geniessen Sie authentische, köstliche thailändische Küche im Herzen des Zürcher Kreises 4.',
  'Hotel Greulich is home to the legendary Thai Food Restaurant 555+. Here, you can enjoy authentic and delicious Thai cuisine in the heart of Zurich’s District 4.'),
 ('Stazione Paradiso', 'https://stazioneparadiso.ch/', 'Im Sommer ist das Stazione Paradiso aus Zürich nicht mehr wegzudenken. Eine lebendige Strandbar direkt an der Limmat.',
  'In the summer, Stazione Paradiso from Zurich is a must-visit. A vibrant beach bar right on the Limmat River.'),
 ('Appenzeller Bier', 'https://appenzellerbier.ch/', 'Ein exzellentes Restaurant braucht ein erstklassiges Bier. Wir sagen nur: Appenzeller! Ein wichtiger Partner seit den Anfängen des Spitz. Vielen Dank!',
  'An excellent restaurant needs top-quality beer. We say only: Appenzeller! An important partner since the early days of Spitz. Thank you!'),
 ('Soeder', 'https://www.soeder.ch/', 'Unser Partner für alles, was gut riecht. Bei uns treffen Sie früher oder später auf diese tollen Produkte, welche alle in Zürich produziert werden.',
  'Our partner for everything that smells wonderful. Sooner or later, you’ll come across these amazing products, all of which are made in Zurich.'),
 ('Stoll Kaffee', 'https://www.stoll-kaffee.ch/', 'Die traditionsreiche Kaffeerösterei aus Zürich versorgt uns kontinuierlich mit ihrem exquisiten Kaffee. Jede getrunkene Tasse offenbart das unvergleichliche Engagement und die Leidenschaft für Kaffee, die in jedem Schluck spürbar ist.',
  'The traditional coffee roastery from Zurich continuously supplies us with its exquisite coffee. Every cup reveals the unparalleled dedication and passion for coffee, which can be felt in every sip.'),
 ('em kraft', 'https://www.emkraft.ch/', 'Im Einklang mit unseren ökologischen Prinzipien nutzen wir im Spitz hauptsächlich em kraft zur Reinigung. Diese Reinigungsprodukte basieren auf effektiven Mikroorganismen und bestehen ausschliesslich aus natürlichen Inhaltsstoffen.',
  'In line with our ecological principles, we primarily use em kraft for cleaning at Spitz. These cleaning products are based on effective microorganisms and consist exclusively of natural ingredients.'),
 ('Jungle Service', 'https://jungleservice.ch/', 'Der Name ist Programm: Unsere Freunde und Partner für alles Grüne im Spitz.',
  'Our friends and partners for everything green at Spitz.'),
]

JOBS = [('Sous Chef:in (m/w/d), Vollzeit im Monatslohn', 'https://link.ostendis.com/publication/sous-chef-monatslohn/4f0ldpctb8ellnlov23m5r2vel4j4x6i0o6jrkb8kkxml26d38lxe3feym3lmo1f'),
        ('Küchenchef:in (m/w/d), Vollzeit im Monatslohn', 'https://link.ostendis.com/publication/kuechenchef-in/dqkabo45gforsidi77va4nsm3hy72149yv5vxrdovy5hxqf6dzdyjlrmre2bacqt'),
        ('Restaurationsfachmann/-frau (m/w/d) im Stundenlohn', 'https://link.ostendis.com/publication/restaurationsfachmann-frau-im-stundenlohn/po0cwl5dr4vil8zs2480pqxrl0gziwncf0iq6trbsifkrapoo270hj8m2o36gfd7')]

HERO = ['main-10', 'main-8', 'main-15', 'main-7', 'main-9', 'main-6', 'main-13', 'main-11', 'main-14', 'main-5', 'main-4', 'main-3', 'main-2', 'main-1']
HALB = '(min-width:881px) 50vw, 100vw'

# ---------------------------------------------------------------- Startseite
def startseite(lang):
    de = lang == 'de'
    L = {
     'karten': [('Mittagskarte Restaurant', '/files/161126.pdf'), ('Abendkarte Restaurant', '/files/Abendkarte_Herbst-Winter_HP-Final2026.pdf'), ('Auswahlmenü Gruppen Winter', '/files/Auswahlmenu_Winter.pdf')]
       if de else [('Lunch menu restaurant', '/files/161126EN.pdf'), ('Evening menu restaurant', '/files/Abendkarte_Herbst-Winter_2026_EN-Final-HP.pdf'), ('Group menu winter (German)', '/files/Auswahlmenu_Winter.pdf')],
     'rest_t': ('Das', 'Restaurant') if de else ('The', 'Restaurant'),
     'rest_p': 'Unsere Küche ist kreativ und zugleich bodenständig, mit tiefem Bezug zur Natur. Im Mittelpunkt stehen saisonale Zutaten aus dem Alpenraum. Es entsteht ehrliches, kraftvolles Essen – archaisch im Charakter, fein im Detail. Dazu servieren wir besondere Weine mit Charakter. So schmeckt’s bei uns.'
       if de else 'Our cuisine is both creative and down-to-earth, deeply connected to nature. The focus lies on seasonal ingredients from the Alpine region. The result is honest, powerful food – rustic in character, refined in detail. We serve distinctive wines with personality to match. That’s how we do things here.',
     'rest_links': [('Abendkarte', '/files/Abendkarte_Herbst-Winter_HP-Final2026.pdf'), ('Weinkarte', '/files/Weinkarte_19.08.pdf'), ('Mittagsmenü', '/files/161126.pdf')]
       if de else [('Evening menu', '/files/Abendkarte_Herbst-Winter_2026_EN-Final-HP.pdf'), ('Wine menu', '/files/Weinkarte_19.08.pdf'), ('Lunch menu', '/files/061126_EN.pdf')],
     'pille1': ('Lunch &amp; Dinner<small>bis 45 Personen</small>' if de else 'Lunch &amp; Dinner<small>up to 45 people</small>'),
     'pille2': ('Alle anderen Anlässe' if de else 'All other events'),
     'ter_t': ('Die', 'Terrasse') if de else ('The', 'Terrace'),
     'ter_p': 'Urban und unvergesslich. Unsere Terrasse ist eine grüne Oase mitten in Zürich – direkt beim Hauptbahnhof und doch wunderbar ruhig. Umgeben von üppiger Bepflanzung bietet sie einen aussergewöhnlichen Rahmen für entspannte Sommermomente im Spitz. Ein entspannter Lunch, ein stimmungsvolles Abendessen oder ein stilvoller Event im Freien – dieser besondere Ort ist wie gemacht für jeden Anlass.'
       if de else 'Urban and unforgettable. Our terrace is a green oasis in the middle of Zurich – right next to the main train station and yet wonderfully quiet. Surrounded by lush greenery, it provides a unique setting for relaxed summer moments at Spitz. A laid-back lunch, an atmospheric dinner, or a stylish outdoor event – this special place is made for every occasion.',
     'bar_t': ('Unsere', 'Bar') if de else ('Our', 'Bar'),
     'bar_p': ['Für kleinere Runden unter 10 Personen braucht es in unserer Bar keine Reservation: Einfach spontan vorbeikommen, Platz nehmen und den Moment geniessen. Wir freuen uns auf euch.',
               'Gerne <a href="/event#anfrage">reservieren</a> wir für Gruppen ab 10 Personen – ideal für Apéros, kleine Feiern oder den gepflegten Start in einen langen Abend. Es gilt eine Mindestkonsumation von CHF 35.– pro Person – genug Spielraum also für ein gutes Glas, einen kleinen Happen und vielleicht noch eine zweite Runde.']
       if de else ['The bar at Spitz takes you on a journey through the world of spirits. We are especially proud of our centerpiece: an exquisite whisky collection featuring over 250 bottles, including rare gems steeped in history. Additionally, our creative cocktail selection offers the perfect indulgence for every mood.',
               'For groups of 10 or more we are happy to <a href="/en/events#anfrage">reserve</a> a space for you. A minimum spend of CHF 35 per person applies.'],
     'bar_links': [('Barkarte', '/files/Barkarte_2026.pdf'), ('Spirituosenkarte', '/files/Spirituosenkarte_Dezember.pdf')] if de else [('Bar menu', '/files/Barkarte_2026.pdf'), ('Spirits menu', '/files/Spirituosenkarte_Dezember.pdf')],
     'bis_t': ('Das', 'Bistro') if de else ('The', 'Bistro'),
     'bis_p': 'Ob nach einer Ausstellung ein exzellenter Espresso oder ein kurzer Schwatz mit Freunden beim Hauptbahnhof – unser Museumsbistro ist der ideale Treffpunkt. Wir bieten eine Auswahl an unkomplizierten und erschwinglichen Speisen und Getränken, die schnell serviert werden, ohne dabei den Geschmack zu vernachlässigen. Die meisten unserer Produkte bereiten wir mit viel Liebe selbst zu.'
       if de else 'Enjoy an excellent espresso after an exhibition or meet friends for a quick chat at the main train station? In our museum bistro, we offer a selection of simple and affordable food and drinks. Speed is important to us, but our focus is always on flavour. Most of our products are homemade.',
     'anl_t': ('Ihr', 'Anlass') if de else ('Your', 'Event'),
     'anl_pille': 'Ihre Event&shy;anfrage' if de else 'Event request',
     'anl_p': ['Unsere Dienstleistungen decken die gesamte Bandbreite von Beratung und Planung bis hin zur Durchführung verschiedenster Veranstaltungen ab – sowohl geschäftlich als auch privat. Ob Corporate Events, Kulturveranstaltungen, Kongresse oder private Feiern wie Geburtstage und Hochzeiten – wir sorgen dafür, dass Ihr Event rundum gelingt.',
               'Benötigen Sie weitere Informationen oder Unterstützung? Wir helfen Ihnen gerne weiter: <a href="mailto:anlass@restaurantspitz.ch">anlass@restaurantspitz.ch</a>, Telefon <a href="tel:+41442219478">044 221 94 78</a>']
       if de else ['Our services include consulting, planning and executing a wide range of events, both corporate and private. These include corporate events, cultural gatherings, conferences, as well as private occasions such as birthdays and weddings.',
               'Do you need more information or assistance? We’ll be happy to help: <a href="mailto:anlass@restaurantspitz.ch">anlass@restaurantspitz.ch</a>, phone <a href="tel:+41442219478">044 221 94 78</a>'],
     'anl_links': [('Angebot Apéro Frühling | Sommer', '/files/Apero_26.pdf'), ('Angebot Apéro Herbst | Winter', '/files/Apero_26_HerbstWinter.pdf'),
                   ('Angebot Bankette Frühling | Sommer', '/files/Bankette_26_Neu.pdf'), ('Angebot Bankette Herbst | Winter', '/files/Bankette_26_HerbstWinter_II.pdf'), ('Angebot Sitzungen', '/files/Sitzungen_2025.pdf')]
       if de else [('Apéro menu', '/files/Apero_26_AutumnWinter_ENG.pdf'), ('Banquet menu', '/files/Bankette_26_ENG.pdf'), ('Meetings (German)', '/files/Sitzungen_2025.pdf')],
     'zeit_t': 'Öffnungszeiten' if de else 'Opening hours',
     'bes_t': 'Besondere Öffnungszeiten' if de else 'Special opening hours',
     'jobs_p': 'Wir sind immer auf der Suche. Alle unsere freien Stellen werden stets hier veröffentlicht. Sollten momentan keine offenen Positionen verfügbar sein, freuen wir uns jederzeit auf Initiativbewerbungen. Bitte sende diese an: <a href="mailto:bewerben@restaurantspitz.ch">bewerben@restaurantspitz.ch</a>.'
       if de else 'We are always on the lookout. All our job openings are posted here. If there are no available positions at the moment, we welcome unsolicited applications at any time. Please send them to: <a href="mailto:bewerben@restaurantspitz.ch">bewerben@restaurantspitz.ch</a>. Job adverts are in German.',
    }
    ev = '/event' if de else '/en/events'
    def titel(paar, tag='h2', id_=None):
        return f'<{tag} class="titel"{f" id={id_}" if id_ else ""}><span>{e(paar[0])}</span><span class="einzug">{e(paar[1])}</span></{tag}>'

    zeiten = ''.join(f'<div><h3>{n}</h3><dl>{"".join(f"<dt>{d}</dt><dd>{z}</dd>" for d, z in rows)}</dl></div>' for n, rows in ZEITEN[lang])
    besondere = ''.join(f'<li>{e(x)}</li>' for x in BESONDERE[lang])
    friends = ''.join(f'<div><h3>{e(n)}</h3><p>{e(d if de else en)}</p><a href="{u}" target="_blank" rel="noopener">{u.split("//")[1].rstrip("/").replace("www.", "www.") if u.split("//")[1].startswith("www.") else "www." + u.split("//")[1].rstrip("/")}</a></div>' for n, u, d, en in FRIENDS)

    inhalt = f'''
<h1 class="sr">{"Restaurant Spitz Zürich: Restaurant, Bar, Bistro und Anlässe beim Landesmuseum" if de else "Restaurant Spitz Zurich: restaurant, bar, bistro and events at the Swiss National Museum"}</h1>
{karussell(HERO, "Gerichte und Ambiente im Restaurant Spitz" if de else "Dishes and atmosphere at Restaurant Spitz", "100vw", auto=True, hell=True, cls="hero", erstes_eager=True)}
{pfeilliste(L['karten'], 'karten')}

<section class="abschnitt" id="restaurant" aria-labelledby="t-restaurant">
  <div class="split">
    <div>
      <div class="kopfzeile">{titel(L['rest_t'], id_='t-restaurant')}
        <div class="pillen"><a class="pille pink" href="{ALENO[lang]}" target="_blank" rel="noopener">{L['pille1']}</a><a class="pille gruen" href="{ev}">{L['pille2']}</a></div></div>
      <div class="text"><p>{L['rest_p']}</p>{pfeilliste(L['rest_links'])}</div>
    </div>
    <div class="medien">{karussell(['restaurant-2', 'restaurant-1', 'restaurant-4', 'e'], 'Restaurant Spitz', HALB, hell=True)}</div>
  </div>
</section>

<section class="abschnitt" id="terrasse" aria-labelledby="t-terrasse">
  <div class="split">
    <div class="medien hoch">{bild('terrasse-1', 'Terrasse des Spitz mit Pflanzen und Sonnenschirmen' if de else 'The Spitz terrace with plants and parasols', HALB, cls='bild')}</div>
    <div><div class="kopfzeile">{titel(L['ter_t'], id_='t-terrasse')}</div><div class="text"><p>{L['ter_p']}</p></div></div>
  </div>
</section>

<section class="abschnitt" id="bar" aria-labelledby="t-bar">
  <div class="split umgekehrt">
    <div class="medien">{karussell(['bar-2', 'bar-1', 'm', 'c'], 'Bar im Spitz' if de else 'The bar at Spitz', HALB, hell=True)}</div>
    <div><div class="kopfzeile">{titel(L['bar_t'], id_='t-bar')}</div><div class="text">{''.join(f'<p>{p}</p>' for p in L['bar_p'])}{pfeilliste(L['bar_links'])}</div></div>
  </div>
</section>

<section class="abschnitt" id="bistro" aria-labelledby="t-bistro">
  <div class="split">
    <div class="medien">{karussell(['bistro-1', 'bistro-2', 'bistro-3', 'bistro-4', 'bistro-5'], 'Bistro im Landesmuseum' if de else 'Bistro at the museum', HALB, hell=True)}</div>
    <div><div class="kopfzeile">{titel(L['bis_t'], id_='t-bistro')}</div><div class="text"><p>{L['bis_p']}</p></div></div>
  </div>
</section>

<section class="abschnitt" id="anlass" aria-labelledby="t-anlass">
  <div class="split umgekehrt">
    <div class="medien">{karussell(['i', 'anlass-1'], 'Gedeckter Tisch für einen Anlass' if de else 'Table set for an event', HALB, hell=True)}</div>
    <div>
      <div class="kopfzeile">{titel(L['anl_t'], id_='t-anlass')}<div class="pillen"><a class="pille verlauf" href="{ev}#anfrage">{L['anl_pille']}</a></div></div>
      <div class="text">{''.join(f'<p>{p}</p>' for p in L['anl_p'])}{pfeilliste(L['anl_links'])}</div>
    </div>
  </div>
</section>

<section class="zeiten" id="oeffnungszeiten" aria-labelledby="t-zeiten">
  <h2 class="titel" id="t-zeiten">{L['zeit_t']}</h2>
  <div class="zeiten-raster">{zeiten}</div>
</section>
<section class="besondere" aria-labelledby="t-besondere">
  <h3 id="t-besondere">{L['bes_t']}</h3>
  <ul>{besondere}</ul>
</section>

<section class="abschnitt" id="jobs" aria-labelledby="t-jobs">
  <div class="split">
    <div class="medien">{karussell(['jobs-1', 'jobs-2'], 'Service im Restaurant Spitz' if de else 'Service at Restaurant Spitz', HALB, hell=True)}</div>
    <div><div class="kopfzeile"><h2 class="titel" id="t-jobs">Jobs</h2></div><div class="text"><p>{L['jobs_p']}</p>{pfeilliste(JOBS)}</div></div>
  </div>
</section>

<section class="abschnitt" id="friends" aria-labelledby="t-friends">
  <h2 class="titel" id="t-friends" style="padding-inline:var(--rand)">Friends</h2>
  <div class="friends">{friends}{HERZ}</div>
</section>
'''
    return seite(lang, '/' if de else '/en/',
                 'Restaurant Spitz Zürich | Restaurant, Bar, Bistro beim Landesmuseum' if de else 'Restaurant Spitz Zurich | Restaurant, bar and bistro at the Swiss National Museum',
                 'Restaurant, Bar, Bistro und Anlässe im Landesmuseum Zürich, direkt beim Hauptbahnhof. Saisonale Küche aus dem Alpenraum, Weine mit Charakter. Jetzt Tisch reservieren.'
                 if de else 'Restaurant, bar, bistro and events at the Swiss National Museum in Zurich, right next to the main station. Seasonal Alpine cuisine and wines with character. Book a table.',
                 inhalt, aktiv=None, ldjson=LD_RESTAURANT)

# ---------------------------------------------------------------- Event-Formular
def formular(lang, betreff):
    de = lang == 'de'
    l = (lambda d, en_: d if de else en_)
    danke = SITE + ('/danke' if de else '/en/thanks')
    return f'''<form class="formular" action="https://api.web3forms.com/submit" method="post">
  <input type="hidden" name="access_key" value="{WEB3FORMS_KEY}">
  <input type="hidden" name="subject" value="{e(betreff)}">
  <input type="hidden" name="from_name" value="Website restaurantspitz.ch">
  <input type="hidden" name="redirect" value="{danke}">
  <input type="checkbox" name="botcheck" class="sr" tabindex="-1" autocomplete="off" aria-hidden="true">
  <div class="feld"><label for="f-person">{l("Ansprechperson", "Contact person")}</label><input id="f-person" name="Ansprechperson" type="text" autocomplete="name" required></div>
  <div class="feld"><label for="f-email">{l("E-Mail", "Email")}</label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
  <div class="feld"><label for="f-telefon">{l("Telefonnummer", "Phone")}</label><input id="f-telefon" name="Telefonnummer" type="tel" autocomplete="tel" required></div>
  <div class="feld"><label for="f-personen">{l("Anzahl Teilnehmer", "Number of guests")}</label><input id="f-personen" name="Anzahl Teilnehmer" type="number" min="1" inputmode="numeric" required></div>
  <div class="feld"><label for="f-datum">{l("Bevorzugtes Datum", "Preferred date")}</label><input id="f-datum" name="Bevorzugtes Datum" type="date" min="2026-11-01" max="2028-12-31" required><input type="hidden" id="f-datum-text" name="Bevorzugtes Datum ausgeschrieben" value=""></div>
  <div class="feld"><label for="f-zeitraum">{l("Zeitraum", "Time of day")}</label><select id="f-zeitraum" name="Zeitraum" required>
    <option value="">{l("Bitte auswählen", "Please select")}</option>
    {''.join(f'<option value="{v}">{l(v, en_)}</option>' for v, en_ in [("Vormittag", "Morning"), ("Mittag", "Lunch"), ("Nachmittag", "Afternoon"), ("Abend", "Evening"), ("Ganzer Tag", "Full day")])}</select></div>
  <div class="feld"><label for="f-datum2">{l("Alternatives Datum (optional)", "Alternative date (optional)")}</label><input id="f-datum2" name="Alternatives Datum" type="date" min="2026-11-01" max="2028-12-31"><input type="hidden" id="f-datum2-text" name="Alternatives Datum ausgeschrieben" value=""></div>
  <div class="feld"><label for="f-datum3">{l("Alternatives Datum 2 (optional)", "Alternative date 2 (optional)")}</label><input id="f-datum3" name="Alternatives Datum 2" type="date" min="2026-11-01" max="2028-12-31"><input type="hidden" id="f-datum3-text" name="Alternatives Datum 2 ausgeschrieben" value=""></div>
  <div class="feld breit"><label for="f-location">Location</label><select id="f-location" name="Location">
    {''.join(f'<option value="{v}"{" selected" if v == "Bitte beraten" else ""}>{l(v, en_)}</option>' for v, en_ in [("Bar", "Bar"), ("Bistro", "Bistro"), ("Restaurant", "Restaurant"), ("Terrasse", "Terrace"), ("Bitte beraten", "Please advise")])}</select></div>
  <div class="feld breit"><label for="f-bemerkungen">{l("Erzählen Sie uns von Ihrem Anlass und Ihren Wünschen (optional)", "Tell us about your event and your wishes (optional)")}</label>
    <textarea id="f-bemerkungen" name="Bemerkungen" rows="5" aria-describedby="f-hilfe" placeholder="{l("Zum Beispiel: «Wir möchten unser Team zu einem gemütlichen, unkomplizierten Abendessen einladen, ohne grosses Programm. Welche Räume kommen für uns in Frage?»", "For example: “We would like to invite our team to a relaxed dinner without a big programme. Which rooms would suit us?”")}"></textarea>
    <p class="hilfe" id="f-hilfe">{l("Festlich, gemütlich oder ausgelassen? Je mehr wir wissen, desto besser passt unser Vorschlag.", "Festive, cosy or lively? The more we know, the better our suggestion will fit.")}</p></div>
  <label class="zustimmung breit"><input type="checkbox" id="f-offerte" name="Offerte" value="Ja, bitte Offerte erstellen"><span>{l("Ich wünsche eine Offerte", "I would like a quote")}</span></label>
  <fieldset class="offerte breit">
    <legend>{l("Für eine Offerte benötigen wir von Ihnen:", "For a quote we need:")}</legend>
    <div class="feld breit"><label for="f-firma">{l("Firma", "Company")}</label><input id="f-firma" name="Firma" type="text" autocomplete="organization"></div>
    <div class="feld breit"><label for="f-strasse">{l("Strasse und Hausnummer", "Street and number")}</label><input id="f-strasse" name="Strasse und Hausnummer" type="text" autocomplete="street-address"></div>
    <div class="feld"><label for="f-plz">{l("PLZ", "Postcode")}</label><input id="f-plz" name="PLZ" type="text" autocomplete="postal-code"></div>
    <div class="feld"><label for="f-ort">{l("Ort", "City")}</label><input id="f-ort" name="Ort" type="text" autocomplete="address-level2"></div>
  </fieldset>
  <label class="zustimmung breit"><input type="checkbox" name="Datenschutz" value="Datenschutzerklärung gelesen und akzeptiert" required>
    <span>{l('Ich habe die <a href="/datenschutz" target="_blank">Datenschutzerklärung</a> gelesen und bin einverstanden.', 'I have read and accept the <a href="/en/privacy" target="_blank">privacy policy</a>.')}</span></label>
  <div class="breit senden"><button class="btn" type="submit">{l("Termin anfragen", "Send request")} <span aria-hidden="true">→</span></button>
    <a class="btn hell" href="tel:+41442219478">+41 44 221 94 78</a></div>
</form>'''

# ---------------------------------------------------------------- Eventseite
EV = {
 'de': dict(
  h1='Ihr Event im Spitz', lead='Firmenanlass, Apéro, Hochzeit oder Kongress: Wir beraten, planen und führen Ihren Anlass durch. Für 10 bis 500 Gäste, mitten in Zürich.',
  warum='Warum bei uns?',
  vier=[('Zentrale Lage und Museumskontext', 'event-1', 'Direkt im Herzen von Zürich gelegen, verbindet das Restaurant Spitz urbanes Flair mit kultureller Atmosphäre. Eingebettet in den Museumskontext entsteht eine besondere Kulisse, die jedem Event eine inspirierende Note verleiht – ob geschäftlich oder privat.'),
        ('Kulinarik & Signature Drinks', 'event-2', 'Unsere Küche steht für saisonale Zutaten, kreative Kompositionen und höchste Qualität. Ergänzt wird das Erlebnis durch sorgfältig kreierte Signature Drinks, die perfekt auf Ihr Event abgestimmt werden – von elegant bis überraschend.'),
        ('Flexible Räume & Grösse', 'event-3', 'Ob kleine Runde oder grosse Gesellschaft: Unsere Räumlichkeiten lassen sich individuell kombinieren und an Ihre Bedürfnisse anpassen. Unterschiedliche Settings ermöglichen Events jeder Art – stilvoll, unkompliziert und genau nach Ihren Vorstellungen.'),
        ('Persönliche Betreuung & Planung', 'event-4', 'Von der ersten Anfrage bis zum letzten Gast stehen wir Ihnen persönlich zur Seite. Unser erfahrenes Team unterstützt Sie bei Planung, Ablauf und Details, damit Sie sich ganz auf Ihre Gäste konzentrieren können.')],
  events='Events',
  drei=[('Firmen & Business', 'events-5', 'Vom Apéro über Workshops bis zum festlichen Dinner – wir bieten den passenden Rahmen für professionelle und stilvolle Business-Events.'),
        ('Private Feiern', 'events-6', 'Ob Geburtstag, Jubiläum oder Hochzeit: Feiern Sie besondere Momente in einzigartiger Atmosphäre und mit individueller Betreuung.'),
        ('Kultur & Museum', 'events-7', 'Nutzen Sie die inspirierende Verbindung von Gastronomie und Kultur für aussergewöhnliche Anlässe mit besonderem Charakter.')],
  raeume_t='Räume und Kapazitäten',
  raeume=[('Restaurant', 'events-8', 'Dinner Party bis 100 Personen', 'Ideal für grössere Gesellschaften oder exklusive Dinner. Grosszügig, lebendig und perfekt für unvergessliche Abende mit bis zu 100 Personen.'),
          ('Bar & Terrasse', 'events-9', 'Apéro & Afterparty', 'Der perfekte Ort für entspannte Apéros und After-Partys. Innen wie aussen geniessen Sie eine lockere Atmosphäre mit stilvollem Ambiente.'),
          ('Bistro', 'events-10', 'Kleinere Events', 'Für kleinere Events im persönlichen Rahmen. Charmant, unkompliziert und ideal für private Feiern oder Business-Lunches.'),
          ('Foyer', 'events-11', 'Grossanlässe bis 500 Personen', 'Ein moderner Raum für Empfang, Apéro oder als Auftakt zu Ihrem Event. Flexibel nutzbar und visuell eindrucksvoll.'),
          ('Willy G.S. Hirzel', 'events-12', 'Firmenanlässe bis 300 Personen', 'Stilvoll und elegant – geschaffen für exklusive Events und besondere Anlässe mit gehobenem Anspruch, auch bei komplexen technischen Anforderungen.')],
  download='Download', downloads=[('FAQ', '/files/Events/FAQ_Anlaesse.pdf'), ('AGB', '/files/Events/AGB_Anlaesse.pdf'), ('Anlassbroschüre', '/files/Events/Anlass_Brochure.pdf')],
  stimmen_t='Das sagen unsere Gäste',
  stimmen=[('Luisa, Berlin', '«Danke für das Zusammenstellen des fabelhaften Menüs und der Weinauswahl. Das ganze Serviceteam war auf Zack und hat keinen Wunsch der Gäste offen gelassen. Grosses Kompliment von meiner Seite – das kann man sich für jedes Event Setup nur wünschen.»'),
           ('Peter, Zürich', '«Grossen Dank für euer Engagement, das gute Gelingen des Events, sowie für den reibungslosen Ablauf und für die geleisteten Überstunden – es war ganz toll. Ich habe viele, viele Komplimente entgegengenommen. Die Besucher:innen haben die Lokalität, den diskreten und aufmerksamen Service, wie auch die zentrale Erreichbarkeit des Ortes sehr geschätzt.»')],
  addons_t='Add-ons',
  addons=[('Aperitif Upgrade', 'icon-1', 'Verfeinern Sie den Empfang Ihrer Gäste mit ausgewählten Häppchen und besonderen Drinks.'),
          ('Signature Drink Package', 'icon-2', 'Individuell abgestimmte Cocktails, die Ihrem Event eine persönliche Note verleihen.'),
          ('Dessert Buffet', 'icon-3', 'Ein süsser Abschluss mit einer vielfältigen Auswahl an Desserts – liebevoll präsentiert.'),
          ('After Event in der Bar', 'icon-4', 'Lassen Sie den Abend entspannt ausklingen – mit Musik, Drinks und guter Stimmung in unserer Bar.')],
  nach_t='Nachhaltigkeit bei unseren Events', nach='Regional, saisonal, respektvoll: Wir arbeiten mit lokalen Produzent:innen, nutzen Lebensmittel ganzheitlich und achten auf kurze Wege. Genuss mit gutem Gewissen.',
  anfrage_t='Event-Anfrage', anfrage_lead='Die Anfrage dauert eine Minute und ist unverbindlich. Innert 2 Werktagen erhalten Sie unsere persönliche Antwort.',
  jetzt='Jetzt<br> anfragen', betreff='Eventanfrage (Website)'),
 'en': dict(
  h1='Your event at Spitz', lead='Corporate event, apéro, wedding or conference: we advise, plan and run your event. For 10 to 500 guests, right in the centre of Zurich.',
  warum='Why choose us?',
  vier=[('Central location in a museum setting', 'event-1', 'Located in the heart of Zurich, Restaurant Spitz combines urban flair with a cultural atmosphere. Set within the Swiss National Museum, it offers a special backdrop that gives every event an inspiring touch, whether business or private.'),
        ('Cuisine & signature drinks', 'event-2', 'Our kitchen stands for seasonal ingredients, creative compositions and the highest quality. The experience is rounded off by carefully crafted signature drinks, tailored to your event: from elegant to surprising.'),
        ('Flexible rooms & sizes', 'event-3', 'Whether a small gathering or a large party: our rooms can be combined individually and adapted to your needs. Different settings make every kind of event possible: stylish, uncomplicated and exactly as you imagine it.'),
        ('Personal support & planning', 'event-4', 'From the first enquiry to the last guest, we are at your side. Our experienced team supports you with planning, schedule and details, so you can focus entirely on your guests.')],
  events='Events',
  drei=[('Corporate & business', 'events-5', 'From apéros and workshops to festive dinners, we offer the right setting for professional and stylish business events.'),
        ('Private celebrations', 'events-6', 'Birthday, anniversary or wedding: celebrate special moments in a unique atmosphere with personal service.'),
        ('Culture & museum', 'events-7', 'Use the inspiring combination of gastronomy and culture for extraordinary events with a special character.')],
  raeume_t='Rooms and capacities',
  raeume=[('Restaurant', 'events-8', 'Dinner party up to 100 guests', 'Ideal for larger parties or exclusive dinners. Spacious, lively and perfect for unforgettable evenings with up to 100 guests.'),
          ('Bar & terrace', 'events-9', 'Apéro & after party', 'The perfect place for relaxed apéros and after parties. Indoors and outdoors you enjoy a laid-back atmosphere in a stylish setting.'),
          ('Bistro', 'events-10', 'Smaller events', 'For smaller events in a personal setting. Charming, uncomplicated and ideal for private celebrations or business lunches.'),
          ('Foyer', 'events-11', 'Large events up to 500 guests', 'A modern space for receptions, apéros or as the start of your event. Flexible and visually impressive.'),
          ('Willy G.S. Hirzel', 'events-12', 'Corporate events up to 300 guests', 'Stylish and elegant, made for exclusive events and special occasions with high standards, including complex technical requirements.')],
  download='Download', downloads=[('FAQ (German)', '/files/Events/FAQ_Anlaesse.pdf'), ('Terms (German)', '/files/Events/AGB_Anlaesse.pdf'), ('Event brochure', '/files/Events/Anlass_Brochure.pdf')],
  stimmen_t='What our guests say',
  stimmen=[('Luisa, Berlin', '“Thank you for putting together the fabulous menu and wine selection. The whole service team was on the ball and left no wish unfulfilled. Big compliments from my side: that is what you want for every event.”'),
           ('Peter, Zurich', '“Many thanks for your commitment, the success of the event, the smooth running and the extra hours you put in. It was really great. I received many, many compliments. The guests greatly appreciated the venue, the discreet and attentive service and the central location.”')],
  addons_t='Add-ons',
  addons=[('Aperitif upgrade', 'icon-1', 'Refine your guests’ welcome with selected canapés and special drinks.'),
          ('Signature drink package', 'icon-2', 'Individually tailored cocktails that give your event a personal touch.'),
          ('Dessert buffet', 'icon-3', 'A sweet finale with a varied selection of desserts, lovingly presented.'),
          ('After event in the bar', 'icon-4', 'Let the evening wind down with music, drinks and a good mood in our bar.')],
  nach_t='Sustainability at our events', nach='Regional, seasonal, respectful: we work with local producers, use food holistically and keep transport routes short. Enjoyment with a clear conscience.',
  anfrage_t='Event request', anfrage_lead='The request takes a minute and is non-binding. You will receive our personal reply within 2 working days.',
  jetzt='Send<br> request', betreff='Event request (website, EN)'),
}

def eventseite(lang):
    d = EV[lang]; de = lang == 'de'
    vier = ''.join(f'<article><h3>{e(t)}</h3>{bild(b, "", "(min-width:1001px) 25vw, (min-width:521px) 50vw, 100vw")}<p>{e(p)}</p></article>' for t, b, p in d['vier'])
    drei = ''.join(f'<article class="rund">{bild(b, "", "240px")}<h3>{e(t)}</h3><p>{e(p)}</p></article>' for t, b, p in d['drei'])
    raeume = ''.join(f'<article><h3>{e(t)}</h3><a class="kachel" href="#anfrage">{bild(b, t, "(min-width:901px) 33vw, (min-width:561px) 50vw, 100vw")}</a><p class="unter">{e(u)}</p><p>{e(p)}</p></article>' for t, b, u, p in d['raeume'])
    raeume += f'<article><h3>{d["download"]}</h3><div class="download">{"".join(f"<a href=\"{u}\" target=\"_blank\" rel=\"noopener\">{e(n)}</a>" for n, u in d["downloads"])}</div></article>'
    stimmen = ''.join(f'<figure><figcaption>{e(n)}</figcaption><blockquote>{e(z)}</blockquote></figure>' for n, z in d['stimmen'])
    addons = ''.join(f'<article>{bild(b, "", "170px")}<h3>{e(t)}</h3><p>{e(p)}</p></article>' for t, b, p in d['addons'])
    inhalt = f'''
<style>.reservieren{{display:none}}</style>
<a class="reservieren" style="display:flex" href="#anfrage">{d['jetzt']}<span class="pfeil" aria-hidden="true"></span></a>
<header class="ev-kopf"><h1>{e(d['h1'])}</h1><p>{e(d['lead'])}</p></header>
<section class="abschnitt wrap"><h2 class="ev-titel">{e(d['warum'])}</h2><div class="vier">{vier}</div></section>
<section class="band"><div class="wrap"><h2 class="ev-titel">{e(d['events'])}</h2><div class="drei">{drei}</div></div></section>
<section class="abschnitt wrap"><h2 class="ev-titel">{e(d['raeume_t'])}</h2><div class="raeume">{raeume}</div>
  <div class="zweibild">{bild('events-13', '', '(min-width:700px) 50vw, 100vw')}{bild('events-14', '', '(min-width:700px) 50vw, 100vw')}</div></section>
<section class="abschnitt wrap"><h2 class="ev-titel">{e(d['stimmen_t'])}</h2><div class="stimmen">{stimmen}</div></section>
<section class="abschnitt wrap"><h2 class="ev-titel">{e(d['addons_t'])}</h2><div class="addons">{addons}</div>
  <div class="nachhaltig"><img src="/bilder/nachhaltigkeit.svg" alt="" width="180" height="180" loading="lazy"><div><h2>{e(d['nach_t'])}</h2><p>{e(d['nach'])}</p></div></div></section>
<section class="anfrage-bereich wrap" id="anfrage"><h2 class="ev-titel">{e(d['anfrage_t'])}</h2><p class="einleitung">{e(d['anfrage_lead'])}</p>{formular(lang, d['betreff'])}</section>
'''
    pfad = '/event' if de else '/en/events'
    return seite(lang, pfad, ('Events im Spitz Zürich | Firmenanlass, Apéro, Bankett' if de else 'Events at Spitz Zurich | Corporate events, apéros, banquets'),
                 ('Anlässe für 10 bis 500 Gäste im Landesmuseum Zürich: Restaurant, Bar, Bistro, Foyer und Hirzel-Saal. Persönliche Planung, Antwort innert 2 Werktagen.'
                  if de else 'Events for 10 to 500 guests at the Swiss National Museum in Zurich: restaurant, bar, bistro, foyer and Hirzel hall. Personal planning, reply within 2 working days.'),
                 inhalt, aktiv=pfad)

# ---------------------------------------------------------------- Einfache Unterseiten
def unterseite(lang, pfad, titelzeilen, seitentitel, beschreibung, body, breit=False, recht=False):
    tz = ''.join(f'<span>{e(z)}</span>' for z in titelzeilen)
    klass = 'lauftext' + (' breit' if breit else '') + (' recht' if recht else '')
    inhalt = f'<section class="seite"><h1 class="titel">{tz}</h1><div class="{klass}">{body}</div></section>'
    return seite(lang, pfad, seitentitel, beschreibung, inhalt, aktiv=pfad)

def gutscheine(lang):
    de = lang == 'de'
    body = (('<p>Unsere Gutscheine werden bequem über PayPal bezahlt. Nach erfolgreicher Zahlung machen wir uns direkt an die Arbeit, und Sie bekommen den Gutschein in den nächsten Tagen per Post zugeschickt.</p>'
             '<p>Sie haben besondere Wünsche für den Text auf dem Gutschein? Oder kein PayPal-Konto? Kein Problem, schreiben Sie uns einfach an <a href="mailto:info@restaurantspitz.ch">info@restaurantspitz.ch</a>.</p>')
            if de else
            ('<p>Our gift vouchers are paid via PayPal. Once the payment goes through, we get to work right away and send your voucher by post within the next few days.</p>'
             '<p>Got a special message you’d like on the voucher? Or no PayPal account? No worries, just drop us a line at <a href="mailto:info@restaurantspitz.ch">info@restaurantspitz.ch</a>.</p>'))
    ret = SITE + ('/gutscheinbestellung' if de else '/en/voucher-order')
    body += f'''<form class="formular" action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_top" style="grid-template-columns:1fr">
  <input type="hidden" name="business" value="office@restaurantspitz.ch"><input type="hidden" name="currency_code" value="CHF">
  <input type="hidden" name="item_name" value="{'Gutschein Restaurant Spitz' if de else 'Gift voucher Restaurant Spitz'}"><input type="hidden" name="cmd" value="_xclick">
  <input type="hidden" name="lc" value="CH"><input type="hidden" name="return" value="{ret}"><input type="hidden" name="cancel_return" value="{SITE}{'/gutscheine' if de else '/en/vouchers'}">
  <div class="feld" style="max-width:320px"><label for="pp-betrag">{'Betrag in CHF' if de else 'Amount in CHF'}</label>
    <input id="pp-betrag" name="amount" type="number" min="20" step="10" inputmode="numeric" placeholder="{'z. B. 100' if de else 'e.g. 100'}" required></div>
  <div class="senden"><button class="btn" type="submit">{'Jetzt kaufen' if de else 'Buy now'} <span aria-hidden="true">→</span></button></div>
</form>
<img class="zahlarten" src="/bilder/paypal-zahlungsarten.jpg" alt="{'Zahlungsarten: Mastercard, Visa, PayPal, Giropay' if de else 'Payment methods: Mastercard, Visa, PayPal, Giropay'}" width="200" loading="lazy">'''
    return unterseite(lang, '/gutscheine' if de else '/en/vouchers', ['Schenken', 'macht', 'Freude.'] if de else ['Gifting', 'brings', 'joy.'],
                      'Gutscheine | Restaurant Spitz Zürich' if de else 'Gift vouchers | Restaurant Spitz Zurich',
                      'Gutschein für das Restaurant Spitz in Zürich bestellen und per Post erhalten.' if de else 'Order a gift voucher for Restaurant Spitz in Zurich, delivered by post.', body)

def newsletter(lang):
    de = lang == 'de'
    body = (f'<p>{"Melden Sie sich hier für unseren Newsletter an. Wir informieren Sie gelegentlich mit einer Mail mit allen Neuigkeiten rund um den Spitz." if de else "Sign up for our newsletter here. We will occasionally send you an email with all the latest news about Spitz."}</p>'
            f'''<form class="formular" action="https://restaurantspitz.us14.list-manage.com/subscribe/post?u=e913206ec3f0146a52a8f3ac2&amp;id=0518537dff&amp;f_id=00a1b7e5f0" method="post" target="_blank">
  <div class="feld"><label for="mce-FNAME">{'Vorname' if de else 'First name'}</label><input id="mce-FNAME" name="FNAME" type="text" autocomplete="given-name" required></div>
  <div class="feld"><label for="mce-LNAME">{'Nachname' if de else 'Last name'}</label><input id="mce-LNAME" name="LNAME" type="text" autocomplete="family-name" required></div>
  <div class="feld breit"><label for="mce-EMAIL">{'E-Mail' if de else 'Email'}</label><input id="mce-EMAIL" name="EMAIL" type="email" autocomplete="email" required></div>
  <div aria-hidden="true" style="position:absolute;left:-5000px"><input type="text" name="b_e913206ec3f0146a52a8f3ac2_0518537dff" tabindex="-1" value=""></div>
  <div class="breit senden"><button class="btn" type="submit">{'Anmelden' if de else 'Subscribe'} <span aria-hidden="true">→</span></button></div>
</form>''')
    return unterseite(lang, '/newsletter' if de else '/en/newsletter', ['Sie werden', 'von uns', 'hören.'] if de else ['You will', 'hear', 'from us.'],
                      'Newsletter | Restaurant Spitz Zürich' if de else 'Newsletter | Restaurant Spitz Zurich',
                      'Neuigkeiten aus dem Restaurant Spitz per Mail erhalten.' if de else 'Get news from Restaurant Spitz by email.', body)

def kontakt(lang):
    de = lang == 'de'
    body = (f'<p>{"Gerne können Sie uns hier per Mail oder Telefon kontaktieren. Wir freuen uns immer über Anregungen oder konstruktive Kritik und sind für alle allgemeinen Fragen immer für Sie da." if de else "Feel free to contact us by email or phone. We always appreciate suggestions or constructive feedback and are happy to help with any general enquiries."}</p>'
            f'<p><strong>Spitz</strong><br>Museumstrasse 2<br>8001 Zürich<br>{"im Landesmuseum, beim Hauptbahnhof" if de else "at the Swiss National Museum, next to the main station"}</p>'
            f'<p><strong>{"Restaurant, Bar, Bistro" if de else "Restaurant, bar, bistro"}</strong><br><a href="tel:+41442219477">044 221 94 77</a><br><a href="mailto:info@restaurantspitz.ch">info@restaurantspitz.ch</a></p>'
            f'<p><strong>{"Anlässe" if de else "Events"}</strong><br><a href="tel:+41442219478">044 221 94 78</a><br><a href="mailto:anlass@restaurantspitz.ch">anlass@restaurantspitz.ch</a></p>'
            f'<p>{"Für Tischreservationen nutzen Sie bitte unser" if de else "To book a table, please use our"} <a href="{ALENO[lang]}" target="_blank" rel="noopener">{"Online-Reservationstool" if de else "online booking tool"}</a>.</p>'
            f'<p><a class="btn hell" href="https://maps.google.com/?q=Restaurant+Spitz+Museumstrasse+2+8001+Z%C3%BCrich" target="_blank" rel="noopener">{"Route planen" if de else "Get directions"} <span aria-hidden="true">→</span></a></p>')
    return unterseite(lang, '/kontakt' if de else '/en/contact', ['Grüezi.'] if de else ['Hello.'],
                      'Kontakt | Restaurant Spitz Zürich' if de else 'Contact | Restaurant Spitz Zurich',
                      'Kontakt Restaurant Spitz, Museumstrasse 2, 8001 Zürich. Telefon 044 221 94 77.' if de else 'Contact Restaurant Spitz, Museumstrasse 2, 8001 Zurich. Phone +41 44 221 94 77.', body)

def impressum(lang):
    de = lang == 'de'
    body = ('<p>Spunten AG<br>Museumstrasse 2<br>8001 Zürich</p><p>Telefon <a href="tel:+41442219477">+41 44 221 94 77</a><br>E-Mail <a href="mailto:info@restaurantspitz.ch">info@restaurantspitz.ch</a></p><p>Eingetragen im Schweizerischen Handelsregister<br>Umsatzsteuer-Identifikationsnummer CHE-463.638.587</p>'
            if de else '<p>Spunten AG<br>Museumstrasse 2<br>8001 Zurich</p><p>Phone <a href="tel:+41442219477">+41 44 221 94 77</a><br>Email <a href="mailto:info@restaurantspitz.ch">info@restaurantspitz.ch</a></p><p>Registered in the Swiss Commercial Register<br>VAT number CHE-463.638.587</p>')
    return unterseite(lang, '/impressum' if de else '/en/impressum', ['Impressum'] if de else ['Imprint'], 'Impressum | Restaurant Spitz' if de else 'Imprint | Restaurant Spitz', 'Impressum Restaurant Spitz, Spunten AG.', body)

def agb(lang):
    de = lang == 'de'
    body = ('<p>Für Anlässe gelten unsere Allgemeinen Geschäftsbedingungen:</p>' if de else '<p>Our general terms and conditions apply to events (German):</p>') + \
           pfeilliste([('AGB Anlässe (PDF)' if de else 'Terms and conditions for events (PDF)', '/files/Events/AGB_Anlaesse.pdf'), ('FAQ Anlässe (PDF)' if de else 'Event FAQ (PDF)', '/files/Events/FAQ_Anlaesse.pdf')])
    return unterseite(lang, '/agb' if de else '/en/agb', ['AGB'] if de else ['Terms'], 'AGB | Restaurant Spitz' if de else 'Terms | Restaurant Spitz', 'Allgemeine Geschäftsbedingungen Restaurant Spitz.', body)

def datenschutz(lang):
    de = lang == 'de'
    body = open(os.path.join(ROOT, '_quellen', 'ds_de.html' if de else 'ds_en.html'), encoding='utf-8').read()
    return unterseite(lang, '/datenschutz' if de else '/en/privacy', ['Datenschutz'] if de else ['Privacy'],
                      'Datenschutzerklärung | Restaurant Spitz' if de else 'Privacy policy | Restaurant Spitz', 'Datenschutzerklärung der Spunten AG.', body, breit=True, recht=True)

def gutscheinbestellung(lang):
    de = lang == 'de'
    body = ('<p>Vielen Dank für Ihre Gutscheinbestellung! Diese ist erfolgreich bei uns eingegangen und wird bearbeitet.</p><p>Den Gutschein erhalten Sie in den nächsten Tagen per Post. Haben Sie individuelle Wünsche, was auf dem Gutschein stehen soll? Kontaktieren Sie uns unter <a href="mailto:info@restaurantspitz.ch">info@restaurantspitz.ch</a>.</p>'
            if de else '<p>Thank you for your voucher order! We have received it and are processing it.</p><p>You will receive the voucher by post in the next few days. Would you like a personal message on it? Contact us at <a href="mailto:info@restaurantspitz.ch">info@restaurantspitz.ch</a>.</p>')
    return unterseite(lang, '/gutscheinbestellung' if de else '/en/voucher-order', ['Vielen', 'Dank.'] if de else ['Thank', 'you.'], 'Gutscheinbestellung | Restaurant Spitz' if de else 'Voucher order | Restaurant Spitz', '', body)

def danke(lang):
    de = lang == 'de'
    body = (f'<p>Ihre Anfrage ist bei uns angekommen. Innert 2 Werktagen erhalten Sie unsere persönliche Antwort.</p><p><a class="btn" href="/">Zur Startseite</a></p>'
            if de else f'<p>Your request has reached us. You will receive our personal reply within 2 working days.</p><p><a class="btn" href="/en/">Back to home</a></p>')
    return unterseite(lang, '/danke' if de else '/en/thanks', ['Vielen', 'Dank.'] if de else ['Thank', 'you.'], 'Vielen Dank | Restaurant Spitz' if de else 'Thank you | Restaurant Spitz', '', body)

def fehler404():
    body = '<p>Diese Seite gibt es nicht (mehr). This page does not exist.</p><p><a class="btn" href="/">Zur Startseite</a> <a class="btn hell" href="/en/">English</a></p>'
    return unterseite('de', '/404', ['Oops.'], 'Seite nicht gefunden | Restaurant Spitz', '', body)

# ---------------------------------------------------------------- Schreiben
DATEIEN = {
 'index.html': startseite('de'), 'en/index.html': startseite('en'),
 'event.html': eventseite('de'), 'en/events.html': eventseite('en'),
 'gutscheine.html': gutscheine('de'), 'en/vouchers.html': gutscheine('en'),
 'gutscheinbestellung.html': gutscheinbestellung('de'), 'en/voucher-order.html': gutscheinbestellung('en'),
 'newsletter.html': newsletter('de'), 'en/newsletter.html': newsletter('en'),
 'kontakt.html': kontakt('de'), 'en/contact.html': kontakt('en'),
 'impressum.html': impressum('de'), 'en/impressum.html': impressum('en'),
 'agb.html': agb('de'), 'en/agb.html': agb('en'),
 'datenschutz.html': datenschutz('de'), 'en/privacy.html': datenschutz('en'),
 'danke.html': danke('de'), 'en/thanks.html': danke('en'),
 '404.html': fehler404(),
}
os.makedirs(os.path.join(ROOT, 'en'), exist_ok=True)
for name, inhalt in DATEIEN.items():
    with open(os.path.join(ROOT, name), 'w', encoding='utf-8') as f:
        f.write(inhalt)

seiten = [p for p, _ in PAARE if p not in ('/danke', '/gutscheinbestellung')] + [en for _, en in PAARE if en not in ('/en/thanks', '/en/voucher-order')]
with open(os.path.join(ROOT, 'sitemap.xml'), 'w') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    f.write(''.join(f'  <url><loc>{SITE}{p}</loc></url>\n' for p in seiten))
    f.write('</urlset>\n')
print(len(DATEIEN), 'Seiten geschrieben')
