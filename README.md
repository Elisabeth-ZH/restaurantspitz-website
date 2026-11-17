# restaurantspitz.ch (Neubau, statisch)

Nachbau von restaurantspitz.ch als statische Seite für Cloudflare Pages, DE und EN.

- Inhalte ändern: Texte stehen in `build.py`, danach `python3 build.py` ausführen.
- Bilder: `bilder/` (AVIF + WebP), Menükarten und Angebote: `files/` (gleiche Pfade wie bisher).
- Formulare: Event-Anfrage über Web3Forms (Schlüssel geht vorläufig an elisabeth@), Gutschein über PayPal, Newsletter über Mailchimp (wie bisher).
- Tischreservation: aleno (DE- und EN-Link).
- `_redirects` leitet die alten Datenschutz-Adressen um, `_headers` setzt Sicherheits- und Cache-Kopfzeilen.

## Vorschau-Modus

Die Seite dient vorerst nur intern zur Ansicht. `_headers` (X-Robots-Tag) und `robots.txt` sperren Suchmaschinen. Beim Livegang beides zurücksetzen.
