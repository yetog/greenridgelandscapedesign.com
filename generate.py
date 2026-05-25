#!/usr/bin/env python3
"""
GreenRidge Landscape & Design - Static Site Generator
Run: python3 generate.py
Generates all pages from site.config.json + templates
"""

import json, os, re, shutil

# ── Load config ───────────────────────────────────────────
with open("site.config.json", encoding="utf-8") as f:
    cfg = json.load(f)

B = cfg["brand"]
SERVICES = cfg["services"]
AREAS = cfg["serviceAreas"]
REVIEWS = cfg["reviews"]
FAQS = cfg["faqs"]
GALLERY = cfg.get("gallery", [])

PHONE = B["phone"]
PHONE_RAW = B["phoneRaw"]
NAME = B["name"]
ADDRESS = f"{B['address']}, {B['city']}, {B['state']} {B['zip']}"
PRIMARY = B["primaryColor"]
SECONDARY = B["secondaryColor"]
WEBHOOK = B["zapierWebhook"]
FONT    = B.get("font", "Inter")

# ── Lucide icon helpers ───────────────────────────────────
def _svg(paths, size=16):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}"'
            f' viewBox="0 0 24 24" fill="none" stroke="currentColor"'
            f' stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
            f' aria-hidden="true">{paths}</svg>')

ICON = {
    'phone':    _svg("<path d='M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.1 12 19.79 19.79 0 0 1 1.1 3.38 2 2 0 0 1 3.08 1h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L7.09 8.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 21 16z'/>"),
    'pin':      _svg("<path d='M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z'/><circle cx='12' cy='10' r='3'/>"),
    'clock':    _svg("<circle cx='12' cy='12' r='10'/><polyline points='12 6 12 12 16 14'/>"),
    'star':     _svg("<polygon points='12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2'/>"),
    'shield':   _svg("<path d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'/><path d='m9 12 2 2 4-4'/>"),
    'home':     _svg("<path d='m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'/><polyline points='9 22 9 12 15 12 15 22'/>"),
    'dollar':   _svg("<line x1='12' x2='12' y1='2' y2='22'/><path d='M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6'/>"),
    'check':    _svg("<polyline points='20 6 9 17 4 12'/>"),
    'check-circle': _svg("<path d='M22 11.08V12a10 10 0 1 1-5.93-9.14'/><polyline points='22 4 12 14.01 9 11.01'/>"),
    'clipboard':_svg("<rect width='8' height='4' x='8' y='2' rx='1'/><path d='M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2'/><path d='M12 11h4'/><path d='M12 16h4'/>"),
    'camera':   _svg("<path d='M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3z'/><circle cx='12' cy='13' r='3'/>"),
    'timer':    _svg("<line x1='10' x2='14' y1='2' y2='2'/><line x1='12' x2='15' y1='14' y2='11'/><circle cx='12' cy='14' r='8'/>"),
    'ruler':    _svg("<path d='M21.3 8.7 8.7 21.3c-1 1-2.5 1-3.4 0l-2.6-2.6c-1-1-1-2.5 0-3.4L15.3 2.7c1-1 2.5-1 3.4 0l2.6 2.6c1 1 1 2.5 0 3.4Z'/><path d='m7.5 10.5 2 2'/><path d='m10.5 7.5 2 2'/><path d='m13.5 4.5 2 2'/><path d='m4.5 13.5 2 2'/>"),
    'phone_lg': _svg("<path d='M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.1 12 19.79 19.79 0 0 1 1.1 3.38 2 2 0 0 1 3.08 1h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L7.09 8.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 21 16z'/>", 24),
    'pin_lg':   _svg("<path d='M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z'/><circle cx='12' cy='10' r='3'/>", 24),
    'clock_lg': _svg("<circle cx='12' cy='12' r='10'/><polyline points='12 6 12 12 16 14'/>", 24),
    'timer_lg': _svg("<line x1='10' x2='14' y1='2' y2='2'/><line x1='12' x2='15' y1='14' y2='11'/><circle cx='12' cy='14' r='8'/>", 24),
    'star_lg':  _svg("<polygon points='12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2'/>", 20),
    'dollar_lg':_svg("<line x1='12' x2='12' y1='2' y2='22'/><path d='M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6'/>", 24),
    'ruler_lg': _svg("<path d='M21.3 8.7 8.7 21.3c-1 1-2.5 1-3.4 0l-2.6-2.6c-1-1-1-2.5 0-3.4L15.3 2.7c1-1 2.5-1 3.4 0l2.6 2.6c1 1 1 2.5 0 3.4Z'/><path d='m7.5 10.5 2 2'/><path d='m10.5 7.5 2 2'/><path d='m13.5 4.5 2 2'/><path d='m4.5 13.5 2 2'/>", 24),
    'home_lg':  _svg("<path d='m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'/><polyline points='9 22 9 12 15 12 15 22'/>", 24),
    'shield_lg':_svg("<path d='M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z'/><path d='m9 12 2 2 4-4'/>", 24),
    'clipboard_lg': _svg("<rect width='8' height='4' x='8' y='2' rx='1'/><path d='M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2'/><path d='M12 11h4'/><path d='M12 16h4'/>", 24),
    'check_lg': _svg("<polyline points='20 6 9 17 4 12'/>", 20),
    'check-circle_lg': _svg("<path d='M22 11.08V12a10 10 0 1 1-5.93-9.14'/><polyline points='22 4 12 14.01 9 11.01'/>", 24),
}
# ─────────────────────────────────────────────────────────


pages_created = []
pages_failed = []

# ── Helpers ───────────────────────────────────────────────

def make_theme_css():
    primary_dark   = B.get("primaryDark", B["primaryColor"])
    secondary_dark = B.get("secondaryDark", B["secondaryColor"])
    accent_color   = B.get("accentColor", "#F5F0E8")
    text_color     = B.get("textColor", "#1A1A1A")
    content = f"""/* Auto-generated by generate.py - do not edit manually */
:root {{
  --green:        {B["primaryColor"]};
  --green-dark:   {primary_dark};
  --green-light:  {B["secondaryColor"]};
  --green-hover:  {secondary_dark};
  --cream:        {accent_color};
  --text:         {text_color};
}}
"""
    write("css/theme.css", content)

def mkdir(path):
    os.makedirs(path, exist_ok=True)

def write(path, content):
    d = os.path.dirname(path)
    if d:
        mkdir(d)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    pages_created.append(path.replace(os.getcwd() + "/", ""))

def nav(active=""):
    service_links = "\n".join(
        f'<li><a href="/services/{s["slug"]}/">{s["name"]}</a></li>'
        for s in SERVICES
    )
    mobile_service_links = "\n".join(
        f'<a href="/services/{s["slug"]}/">{s["name"]}</a>'
        for s in SERVICES
    )
    return f"""
<header class="site-header">
  <nav class="main-nav" aria-label="Main navigation">
    <div class="container nav-inner">
      <a href="/" class="nav-logo">
        <img src="/images/logo.png" alt="{NAME} logo" height="96" />
      </a>
      <ul class="nav-links">
        <li class="has-dropdown">
          <a href="/services/" class="{'active' if active=='services' else ''}">Services ▾</a>
          <ul class="dropdown">
            <li><span class="dropdown-label">Our Services</span></li>
            {service_links}
            <li><a href="/services/" class="dropdown-all">View All Services →</a></li>
          </ul>
        </li>
        <li><a href="/about/" class="{'active' if active=='about' else ''}">About Us</a></li>
        <li><a href="/service-areas/" class="{'active' if active=='areas' else ''}">Service Areas</a></li>
        <li><a href="/reviews/" class="{'active' if active=='reviews' else ''}">Reviews</a></li>
        <li><a href="/faq/" class="{'active' if active=='faq' else ''}">FAQ</a></li>
      </ul>
      <div class="nav-cta">
        <a href="tel:{PHONE_RAW}" class="nav-phone">{PHONE}</a>
        <a href="/request-service.html" class="btn btn-primary btn-sm">Get Started</a>
      </div>
      <button class="hamburger" id="hamburger" aria-label="Open menu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </nav>
</header>
<div class="mobile-menu" id="mobile-menu">
  <div class="mobile-menu-header">
    <img src="/images/logo.png" alt="{NAME}" height="40" />
    <button id="mobile-close" aria-label="Close">✕</button>
  </div>
  <a href="/request-service.html" class="btn btn-primary mobile-cta">Get Free Estimate</a>
  <a href="tel:{PHONE_RAW}" class="btn btn-outline mobile-cta">{PHONE}</a>
  <div class="mobile-nav-section">Services</div>
  {mobile_service_links}
  <div class="mobile-nav-section">Company</div>
  <a href="/about/">About Us</a>
  <a href="/service-areas/">Service Areas</a>
  <a href="/reviews/">Reviews</a>
  <a href="/faq/">FAQ</a>
</div>"""

def footer():
    service_links = "\n".join(
        f'<li><a href="/services/{s["slug"]}/">{s["name"]}</a></li>'
        for s in SERVICES
    )
    santa_clara = [a for a in AREAS if a["county"] == "Santa Clara"][:6]
    san_mateo = [a for a in AREAS if a["county"] == "San Mateo"][:6]
    santa_clara_links = "\n".join(f'<li><a href="/service-areas/{a["slug"]}/">{a["name"]}</a></li>' for a in santa_clara)
    san_mateo_links = "\n".join(f'<li><a href="/service-areas/{a["slug"]}/">{a["name"]}</a></li>' for a in san_mateo)
    return f"""
<footer class="site-footer">
  <div class="footer-main">
    <div class="container footer-grid">
      <div class="footer-brand">
        <a href="/"><img src="/images/logo.png" alt="{NAME}" height="72" class="footer-logo" /></a>
        <p>{B.get('footerTagline', f"{NAME} - locally based in {B['city']}, CA.")}</p>
        <a href="tel:{PHONE_RAW}" class="footer-phone">{PHONE}</a>
        <p class="footer-address">{ADDRESS}</p>
        <div class="footer-social">
          <a href="{B['facebook']}" target="_blank" rel="noopener" aria-label="Facebook">
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20"><path d="M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3z"/></svg>
          </a>
          <a href="{B['instagram']}" target="_blank" rel="noopener" aria-label="Instagram">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1.5" fill="currentColor" stroke="none"/></svg>
          </a>
        </div>
      </div>
      <div class="footer-col">
        <h4>Our Services</h4>
        <ul>{service_links}</ul>
      </div>
      <div class="footer-col">
        <h4>Santa Clara County</h4>
        <ul>{santa_clara_links}<li><a href="/service-areas/">All Areas →</a></li></ul>
      </div>
      <div class="footer-col">
        <h4>San Mateo County</h4>
        <ul>{san_mateo_links}<li><a href="/service-areas/">All Areas →</a></li></ul>
      </div>
    </div>
  </div>
  <div class="footer-bottom">
    <div class="container footer-bottom-inner">
      <span>&copy; <span id="yr"></span> {NAME}. All rights reserved.</span>
      <div class="footer-legal">
        <a href="/privacy-policy.html">Privacy Policy</a>
        <a href="/terms.html">Terms of Use</a>
        <a href="/accessibility.html">Accessibility</a>
      </div>
    </div>
  </div>
</footer>
<script>document.getElementById('yr').textContent = new Date().getFullYear();</script>
<script src="/js/main.js"></script>"""

def head(title, desc, canonical, schema=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  <meta name="description" content="{desc}" />
  <link rel="canonical" href="https://{B['domain']}{canonical}" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{desc}" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://{B['domain']}{canonical}" />
  <meta property="og:image" content="/images/hero-bg.jpg" />
  {schema}
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family={FONT.replace(' ', '+')}:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/css/main.css" />
  <link rel="stylesheet" href="/css/theme.css" />
</head>
<body>"""

def booking_form(compact=False):
    service_opts = "\n".join(
        f'<option value="{s["slug"]}">{s["name"]}</option>'
        for s in SERVICES
    )
    if compact:
        return f"""
<div class="booking-card">
  <div class="booking-card-header">
    <h3>Get Your Custom Quote</h3>
    <p>Response within 1 business hour</p>
  </div>
  <form action="{WEBHOOK}" method="POST" class="booking-form" data-phone="{PHONE}">
    <div class="form-group"><label>Name *</label><input type="text" name="name" required placeholder="Your full name" /></div>
    <div class="form-group"><label>Phone *</label><input type="tel" name="phone" required placeholder="{PHONE}" /></div>
    <div class="form-group"><label>Service</label>
      <select name="service"><option value="">Select a service...</option>{service_opts}</select>
    </div>
    <div class="form-group"><label>Details</label><textarea name="message" rows="3" placeholder="Tell us about your project..."></textarea></div>
    <input type="text" name="_gotcha" style="display:none" />
    <input type="hidden" name="_next" value="/thank-you.html" />
    <button type="submit" class="btn btn-primary btn-block">Send Request →</button>
  </form>
</div>"""
    return f"""
<div class="booking-card">
  <div class="booking-card-header">
    <h3>Request a Free Estimate</h3>
    <p>We respond within 1 business hour</p>
  </div>
  <form action="{WEBHOOK}" method="POST" class="booking-form" data-phone="{PHONE}">
    <div class="form-group"><label>Name *</label><input type="text" name="name" required placeholder="Your full name" /></div>
    <div class="form-row">
      <div class="form-group"><label>Phone *</label><input type="tel" name="phone" required placeholder="{PHONE}" /></div>
      <div class="form-group"><label>ZIP Code *</label><input type="text" name="zip" required placeholder="{B['zip']}" maxlength="5" /></div>
    </div>
    <div class="form-group"><label>Email</label><input type="email" name="email" placeholder="you@email.com" /></div>
    <div class="form-group"><label>Service Needed *</label>
      <select name="service" required><option value="">Select a service...</option>{service_opts}<option value="other">Other / Not Sure</option></select>
    </div>
    <div class="form-group"><label>Project Details</label><textarea name="message" rows="4" placeholder="Describe your project, property size, timeline..."></textarea></div>
    <input type="text" name="_gotcha" style="display:none" />
    <input type="hidden" name="_subject" value="New Estimate Request - {NAME}" />
    <input type="hidden" name="_next" value="/thank-you.html" />
    <button type="submit" class="btn btn-primary btn-block">Send My Request →</button>
    <p class="form-disclaimer">We respect your privacy. No spam, ever.</p>
  </form>
</div>"""

def review_cards(city=None):
    cards = []
    for r in REVIEWS:
        loc = city + ", CA" if city else r["location"]
        stars = ICON["star"] * r["rating"]
        parts = r["name"].split()
        initials = (parts[0][0] + parts[-1][0]).upper() if len(parts) > 1 else parts[0][:2].upper()
        cards.append(f"""
    <div class="review-card">
      <div class="review-stars">{stars}</div>
      <p class="review-text">"{r['text']}"</p>
      <div class="review-footer">
        <div class="review-avatar">{initials}</div>
        <div>
          <div class="review-author">{r['name']}</div>
          <div class="review-location">{loc}</div>
        </div>
      </div>
    </div>""")
    return "\n".join(cards)

def service_area_links():
    return "\n".join(
        f'<a href="/service-areas/{a["slug"]}/" class="city-pill">{a["name"]}</a>'
        for a in AREAS
    )

def breadcrumbs(crumbs):
    items = []
    schema_items = []
    for i, (label, url) in enumerate(crumbs):
        if url:
            items.append(f'<li><a href="{url}">{label}</a></li>')
        else:
            items.append(f'<li>{label}</li>')
        if url:
            schema_items.append(f'{{"@type":"ListItem","position":{i+1},"name":"{label}","item":"https://{B["domain"]}{url}"}}')
        else:
            schema_items.append(f'{{"@type":"ListItem","position":{i+1},"name":"{label}"}}')
    schema = f"""<script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{",".join(schema_items)}]}}
  </script>"""
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb"><div class="container"><ol class="breadcrumb-list">{"".join(items)}</ol></div></nav>', schema

LOCAL_BIZ_SCHEMA = f"""<script type="application/ld+json">
  {{
    "@context":"https://schema.org",
    "@type":"{B.get('schemaType','LocalBusiness')}",
    "name":"{NAME}",
    "url":"https://{B['domain']}/",
    "telephone":"{PHONE}",
    "address":{{"@type":"PostalAddress","streetAddress":"{B['address']}","addressLocality":"{B['city']}","addressRegion":"{B['state']}","postalCode":"{B['zip']}","addressCountry":"US"}},
    "priceRange":"$$",
    "openingHours":"Mo-Sa 07:00-18:00",
    "geo":{{"@type":"GeoCoordinates","latitude":40.7065,"longitude":-73.6212}},
    "areaServed":{json.dumps([{"@type":"City","name":a["name"]} for a in AREAS])},
    "sameAs":["{B['facebook']}","{B['instagram']}"]
  }}
  </script>"""

# ─────────────────────────────────────────────────────────
# HELPER: Service card header (photo or emoji icon)
# ─────────────────────────────────────────────────────────

def service_card_header(s):
    if s.get("image"):
        return f'<img class="service-card-img" src="{s["image"]}" alt="{s["name"]}" loading="lazy" />'
    return f'<div class="service-card-placeholder" aria-hidden="true"></div>'


# ─────────────────────────────────────────────────────────
# HELPER: Gallery section (Our Work)
# ─────────────────────────────────────────────────────────

def gallery_section():
    if not GALLERY:
        return ""
    items = []
    for item in GALLERY:
        if item.get("src"):
            items.append(f"""      <figure class="gallery-item">
        <img src="{item['src']}" alt="{item['alt']}" loading="lazy" />
        <figcaption>{item['label']}</figcaption>
      </figure>""")
        else:
            items.append(f"""      <div class="gallery-item gallery-placeholder-slot">
        <span class="gallery-slot-icon">{item.get('icon','')}</span>
        <span class="gallery-slot-label">{item['label']}</span>
      </div>""")
    items_html = "\n".join(items)
    return f"""
<!-- OUR WORK -->
<section class="section" id="our-work">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Our Work</span>
      <h2>Recent Projects on the South Bay</h2>
      <p>See the quality of our work across San Jose and the South Bay Area - from custom landscapes and patios to full outdoor renovation projects.</p>
    </div>
    <div class="gallery-grid">
{items_html}
    </div>
    <div class="text-center mt-4">
      <a href="/request-service.html" class="btn btn-primary">Start Your Project</a>
    </div>
  </div>
</section>"""


# ─────────────────────────────────────────────────────────
# PAGE: Homepage
# ─────────────────────────────────────────────────────────

def make_homepage():
    service_cards_list = []
    for s in SERVICES:
        service_cards_list.append(f"""
    <div class="service-card">
      {service_card_header(s)}
      <div class="service-card-body">
        <h3>{s['name']}</h3>
        <p>{s['description']}</p>
        <a href="/services/{s['slug']}/" class="card-link">Learn More →</a>
      </div>
    </div>""")
    service_cards = "\n".join(service_cards_list)

    faq_items = "\n".join(f"""
    <div class="faq-item">
      <button class="faq-question">{f['q']} <span class="faq-icon">+</span></button>
      <div class="faq-answer"><p>{f['a']}</p></div>
    </div>""" for f in FAQS[:5])

    slides = B.get('heroSlides', ['/images/hero-bg.jpg'])
    slide_divs = "\n    ".join(
        f'<div class="hero-slide{" active" if i == 0 else ""}" style="background-image:url(\'{s}\')"></div>'
        for i, s in enumerate(slides)
    )
    dot_buttons = "\n    ".join(
        f'<button class="hero-dot{" active" if i == 0 else ""}" data-slide="{i}" aria-label="Go to slide {i+1}"></button>'
        for i in range(len(slides))
    )

    content = f"""{head(
        f"{B['industry']} in {B['city']}, CA | {NAME} | {PHONE}",
        f"{NAME} provides professional {B['industryLower']} in {B['city']}, CA. Call {PHONE} for a free estimate!",
        "/",
        LOCAL_BIZ_SCHEMA
    )}
{nav()}

<!-- HERO -->
<section class="hero" id="hero-carousel">
  <div class="hero-slides">
    {slide_divs}
  </div>
  <div class="hero-overlay"></div>
  <div class="container">
    <div class="hero-content">
      <span class="hero-brand-name">{NAME}</span>
      <span class="hero-badge">San Jose, CA · San Jose and the South Bay Area</span>
      <h1>{B['tagline']}</h1>
      <p>{B.get('heroSubtext', f'Professional {B.get("industryLower","contracting")} services for the South Bay homeowners. Call {PHONE} for a free estimate.')}</p>
      <div class="hero-actions">
        <a href="/request-service.html" class="btn btn-primary btn-lg">Get a Free Estimate</a>
        <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
      </div>
      <div class="hero-trust">
        <span>5-Star Rated</span>
        <span>Certified &amp; Insured</span>
        <span>San Jose, CA Based</span>
      </div>
    </div>
  </div>
  <div class="hero-slide-dots">
    {dot_buttons}
  </div>
</section>
<script>
(function() {{
  var slides = document.querySelectorAll('#hero-carousel .hero-slide');
  var dots   = document.querySelectorAll('#hero-carousel .hero-dot');
  var cur = 0, timer;
  function goTo(n) {{
    slides[cur].classList.remove('active');
    dots[cur].classList.remove('active');
    cur = (n + slides.length) % slides.length;
    slides[cur].classList.add('active');
    dots[cur].classList.add('active');
  }}
  function next() {{ goTo(cur + 1); }}
  function start() {{ timer = setInterval(next, 5500); }}
  function stop()  {{ clearInterval(timer); }}
  dots.forEach(function(dot, i) {{
    dot.addEventListener('click', function() {{ stop(); goTo(i); start(); }});
  }});
  var hero = document.getElementById('hero-carousel');
  hero.addEventListener('mouseenter', stop);
  hero.addEventListener('mouseleave', start);
  start();
}})();
</script>

<!-- STATS -->
<div class="stats-bar">
  <div class="container stats-grid">
    <div class="stat"><span class="stat-n">10+</span><span class="stat-l">Years on the South Bay</span></div>
    <div class="stat"><span class="stat-n">500+</span><span class="stat-l">Happy Customers</span></div>
    <div class="stat"><span class="stat-n">20+</span><span class="stat-l">Cities Served</span></div>
    <div class="stat"><span class="stat-n">100%</span><span class="stat-l">Satisfaction Guaranteed</span></div>
  </div>
</div>

<!-- BOOKING -->
<section class="booking-section">
  <div class="container booking-wrap">
    <div class="booking-info">
      <span class="eyebrow">Start Your Project</span>
      <h2>See Your Project Plan</h2>
      <p>Quick response - typically within 1 hour. No pressure, no obligation. Just honest pricing from a locally owned the South Bay team.</p>
      <ul>
        <li><span class="icon">{ICON["phone"]}</span><div><strong>Call or text {PHONE}</strong> - Mon–Sat 7am–6pm, quick response guaranteed.</div></li>
        <li><span class="icon">{ICON["home"]}</span><div><strong>On-site consultation</strong> - your property gets a personal walkthrough before anything is quoted.</div></li>
        <li><span class="icon">{ICON["clipboard"]}</span><div><strong>Upfront pricing</strong> - a detailed quote in hand before any work begins. No surprises.</div></li>
        <li><span class="icon">{ICON["check-circle"]}</span><div><strong>100% satisfaction guarantee</strong> - the job isn't done until it meets your standard.</div></li>
      </ul>
    </div>
    <div class="booking-form-col">
      {booking_form(compact=True)}
    </div>
  </div>
</section>

<!-- HOW IT WORKS -->
<section class="section section-light" id="how-it-works">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">How {NAME} Works</span>
      <h2>Your Project, Step by Step</h2>
      <p>Three steps from first contact to a finished outdoor space - designed around your vision, not a template.</p>
    </div>
    <div class="steps-grid">
      <div class="step-card">
        <div class="step-number">1</div>
        <h3 class="step-title">Share Your Vision</h3>
        <p class="step-desc">Tell us about your project - call, text, or fill out the online form. Quick response, typically within 1 hour, to confirm your consultation.</p>
      </div>
      <div class="step-card">
        <div class="step-number">2</div>
        <h3 class="step-title">Expert Assessment</h3>
        <p class="step-desc">A {NAME} specialist visits your property, walks the space with you, and listens to your goals. You receive a detailed quote before any commitment.</p>
      </div>
      <div class="step-card">
        <div class="step-number">3</div>
        <h3 class="step-title">Your Custom Build</h3>
        <p class="step-desc">Once the plan is approved, the crew handles everything - materials, grading, installation, and final cleanup. Your outdoor space, exactly as envisioned.</p>
      </div>
    </div>
    <div class="text-center mt-4">
      <a href="/request-service.html" class="btn btn-primary">Schedule Your Consultation</a>
    </div>
  </div>
</section>

<!-- SERVICES -->
<section class="section" id="services">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">What We Do</span>
      <h2>{B.get('servicesHeadline', f'{B.get("industry","Professional")} Services for the South Bay')}</h2>
      <p>{B.get('servicesSubtext', f'Professional {B.get("industryLower","services")} for the South Bay homeowners and businesses.')}</p>
    </div>
    <div class="service-grid">
      {service_cards}
    </div>
  </div>
</section>

<!-- WHY US -->
<section class="split-section">
  <div class="split-img">
    <img src="/images/Gemini_Generated_Image_xrda4xxrda4xxrda.png" alt="GreenRidge Landscape & Design team - San Jose, CA" />
  </div>
  <div class="split-content">
    <span class="eyebrow">Why {NAME}</span>
    <h2>Local Crew. Serious Craftsmanship.</h2>
    <p>Not a franchise - a locally owned team based in San Jose. Every project gets personal attention from people who take pride in their work.</p>
    <ul class="check-list">
      <li>Certified &amp; insured in California</li>
      <li>Transparent pricing - detailed quote before work begins</li>
      <li>Custom designs built around your property and budget</li>
      <li>100% satisfaction guarantee on every job</li>
    </ul>
    <a href="/about/" class="btn btn-primary">Meet Our Team</a>
  </div>
</section>
{gallery_section()}

<!-- REVIEWS -->
<section class="section section-light" id="reviews">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Reviews</span>
      <h2>See How We've Transformed Local Properties</h2>
    </div>
    <div class="review-grid">
      {review_cards()}
    </div>
    <div class="text-center mt-4">
      <a href="/reviews/" class="btn btn-outline">Read More Reviews</a>
    </div>
  </div>
</section>

<!-- SERVICE AREAS -->
<section class="section">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Service Areas</span>
      <h2>Serving All of the South Bay, CA</h2>
      <p>We cover Santa Clara and San Mateo Counties. Don't see your city? Call us - we likely serve you.</p>
    </div>
    <div class="city-grid">
      {service_area_links()}
    </div>
  </div>
</section>

<!-- FAQ PREVIEW -->
<section class="section section-light">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">FAQ</span>
      <h2>Frequently Asked Questions</h2>
    </div>
    <div class="faq-list">
      {faq_items}
    </div>
    <div class="text-center mt-4">
      <a href="/faq/" class="btn btn-outline">See All FAQs</a>
    </div>
  </div>
</section>

<!-- BLOG RESOURCES -->
<!-- TODO: create /blog/ pages and update these links when ready -->
<section class="section blog-resources">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Learn More</span>
      <h2>Helpful Resources</h2>
      <p>Expert tips and guides for your the South Bay property</p>
    </div>
    <div class="blog-grid">
      <article class="blog-card">
        <h3>What Landscaping Zone Are You in and Why Does It Matter?</h3>
        <p>Before you give up on your garden, learn about hardiness zones and how to choose plants that thrive in your specific the South Bay climate - and what our team recommends for Santa Clara & San Mateo.</p>
        <a href="/blog/landscaping-zones/" class="read-more">Read More →</a>
      </article>
      <article class="blog-card">
        <h3>Outdoor Landscaping Ideas for Every Budget</h3>
        <p>Make the most of your backyard with creative outdoor renovation ideas from our the South Bay team - from custom patio builds to full landscape transformations, for every budget.</p>
        <a href="/blog/outdoor-landscaping-ideas/" class="read-more">Read More →</a>
      </article>
      <article class="blog-card">
        <h3>Why You Should Schedule a Spring Tune-up for Your Lawn</h3>
        <p>If you've neglected your spring lawn maintenance, it may be time to bring in some help. Learn why a professional spring tune-up is essential for the South Bay lawns and what it includes.</p>
        <a href="/blog/spring-lawn-tuneup/" class="read-more">Read More →</a>
      </article>
    </div>
    <div class="text-center mt-4">
      <a href="/blog/" class="btn btn-outline">View All Articles</a>
    </div>
  </div>
</section>

<!-- CTA -->
<section class="cta-banner">
  <div class="container">
    <h2>Ready to Reimagine Your Outdoor Space?</h2>
    <p>No pressure, no obligation - just honest work and fair pricing from a team that knows the South Bay.</p>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Request a Design Review</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>

{footer()}
</body></html>"""
    write("index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Service detail pages
# ─────────────────────────────────────────────────────────

def make_service_page(s):
    bc, bc_schema = breadcrumbs([("Home", "/"), ("Services", "/services/"), (s["name"], None)])
    bullets = "\n".join(f"<li>{b}</li>" for b in s["bullets"])
    other_services = "\n".join(
        f'<a href="/services/{o["slug"]}/" class="related-link">{o["name"]}</a>'
        for o in SERVICES if o["slug"] != s["slug"]
    )
    content = f"""{head(
        f"{s['name']} in {B['city']}, CA | {NAME} | {PHONE}",
        f"Professional {s['name'].lower()} in {B['city']}, CA and all of the South Bay. {NAME} - certified, insured, and locally based. Call {PHONE} for a free estimate.",
        f"/services/{s['slug']}/",
        bc_schema
    )}
{nav(active="services")}
{bc}

<section class="page-hero">
  <div class="container">
    <h1>{s['name']} in {B['city']}, CA</h1>
    <p>{s['heroText']}</p>
    <div class="hero-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white">Call {PHONE}</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="container content-sidebar-layout">
    <div class="content-main">
      <h2>Professional {s['name']} on the South Bay</h2>
      <p>{s['description']} {NAME} has been serving {B['city']} and the South Bay for years, delivering reliable results for homeowners and businesses across Santa Clara and San Mateo Counties.</p>
      <h3>What's Included</h3>
      <ul class="check-list">{bullets}</ul>
      <h3>Why Choose {NAME}?</h3>
      <p>We're locally owned and operated in {B['city']}, CA - not a national franchise. Every job is handled by our trained crew, and we back every service with a 100% satisfaction guarantee.</p>
      <div class="cta-inline">
        <a href="/request-service.html" class="btn btn-primary btn-lg">Get a Free Estimate</a>
        <a href="tel:{PHONE_RAW}" class="btn btn-outline">Call {PHONE}</a>
      </div>
      <h3>Service Areas</h3>
      <p>We provide {s['name'].lower()} throughout the South Bay including:</p>
      <div class="city-grid city-grid-sm">
        {service_area_links()}
      </div>
    </div>
    <aside class="content-sidebar">
      {booking_form(compact=True)}
      <div class="sidebar-contact">
        <h4>Contact Us</h4>
        <p>{ICON["phone"]} <a href="tel:{PHONE_RAW}">{PHONE}</a></p>
        <p>{ICON["pin"]} {ADDRESS}</p>
        <p>{ICON['clock']} {B['hours']}</p>
      </div>
    </aside>
  </div>
</section>

<section class="section section-light">
  <div class="container">
    <h2 class="text-center mb-4">What Customers Say</h2>
    <div class="review-grid">{review_cards()}</div>
  </div>
</section>

<section class="section">
  <div class="container">
    <h2 class="text-center mb-4">Other Services We Offer</h2>
    <div class="related-grid">{other_services}</div>
  </div>
</section>

<section class="cta-banner">
  <div class="container">
    <h2>Need {s['name']} in {B['city']}, CA?</h2>
    <p>Call or fill out the form above - we respond within 1 business hour with a free estimate.</p>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write(f"services/{s['slug']}/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Services hub
# ─────────────────────────────────────────────────────────

def make_services_hub():
    cards_list = []
    for s in SERVICES:
        cards_list.append(f"""
    <div class="service-card">
      {service_card_header(s)}
      <div class="service-card-body">
        <h3><a href="/services/{s['slug']}/">{s['name']}</a></h3>
        <p>{s['description']}</p>
        <a href="/services/{s['slug']}/" class="card-link">Learn More →</a>
      </div>
    </div>""")
    cards = "\n".join(cards_list)

    bc, bc_schema = breadcrumbs([("Home", "/"), ("Services", None)])
    content = f"""{head(
        f"{B['industry']} | {NAME} | {PHONE}",
        f"{NAME} offers professional {B['industryLower']} in {B['city']}, CA. Call {PHONE} for a free estimate.",
        "/services/",
        bc_schema
    )}
{nav(active="services")}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>Our Landscaping Services</h1>
    <p>Landscaping &amp; outdoor renovation for the South Bay homeowners. Custom designs, premium materials, and certified craftsmanship - locally based in {B['city']}, CA.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="service-grid">{cards}</div>
  </div>
</section>
<section class="cta-banner">
  <div class="container">
    <h2>Not Sure What You Need?</h2>
    <p>Call us and describe your property - we'll recommend the right services and give you a free estimate.</p>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("services/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: City / Service Area pages
# ─────────────────────────────────────────────────────────

def make_city_page(area):
    city = area["name"]
    slug = area["slug"]
    county = area["county"]
    nearby = ", ".join(f"<strong>{n}</strong>" for n in area["nearbyAreas"])
    bc, bc_schema = breadcrumbs([("Home", "/"), ("Service Areas", "/service-areas/"), (city, None)])

    city_schema = f"""<script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"LandscapingBusiness",
    "name":"{NAME} - {city}","url":"https://{B['domain']}/service-areas/{slug}/",
    "telephone":"{PHONE}","priceRange":"$$",
    "@type":"{B.get('schemaType','LocalBusiness')}",
    "address":{{"@type":"PostalAddress","addressLocality":"{city}","addressRegion":"{B['state']}","addressCountry":"US"}},
    "areaServed":{{"@type":"City","name":"{city}"}}
  }}
  </script>"""

    service_list = "\n".join(
        f'<li><a href="/services/{s["slug"]}/">{s["name"]} in {city}</a></li>'
        for s in SERVICES
    )

    content = f"""{head(
        f"{B['industry']} in {city}, CA | {NAME} | {PHONE}",
        f"Professional {B['industryLower']} in {city}, CA. {NAME} serves {city} and {county} County. Call {PHONE} for a free estimate.",
        f"/service-areas/{slug}/",
        bc_schema + city_schema
    )}
{nav(active="areas")}
{bc}

<section class="page-hero">
  <div class="container">
    <h1>Landscaping Services in {city}, CA</h1>
    <p>{NAME} serves {city} and surrounding {county} County communities. Call {PHONE} for a free estimate today.</p>
    <div class="hero-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white">Call {PHONE}</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="container content-sidebar-layout">
    <div class="content-main">
      <h2>Your Local Landscaping Experts in {city}</h2>
      <p>When {city} homeowners and businesses need reliable landscaping, they call {NAME}. We're based right here in {B['city']}, just minutes away - not a national franchise sending whoever is available. Our team knows {county} County properties and delivers consistent, high-quality work on every visit.</p>
      <p>From weekly lawn maintenance to complete outdoor renovations, we handle everything for residential and commercial properties throughout {city} and surrounding {county} County.</p>

      <h3>Services We Offer in {city}, CA</h3>
      <ul class="check-list">{service_list}</ul>

      <h3>Areas Near {city} We Also Serve</h3>
      <p>In addition to {city}, we serve {nearby} and more throughout {county} County.
      <a href="/service-areas/">View all service areas →</a></p>
    </div>
    <aside class="content-sidebar">
      {booking_form(compact=True)}
      <div class="sidebar-contact">
        <h4>Contact Us</h4>
        <p>{ICON["phone"]} <a href="tel:{PHONE_RAW}">{PHONE}</a></p>
        <p>{ICON["pin"]} {ADDRESS}</p>
        <p>{ICON['clock']} {B['hours']}</p>
      </div>
    </aside>
  </div>
</section>

<section class="section section-light">
  <div class="container">
    <h2 class="text-center mb-4">What {city} Residents Say</h2>
    <div class="review-grid">{review_cards(city)}</div>
  </div>
</section>

<section class="cta-banner">
  <div class="container">
    <h2>Need Landscaping in {city}, CA?</h2>
    <p>We're nearby and ready. Call or submit the form - response within 1 business hour.</p>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write(f"service-areas/{slug}/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Service Areas hub
# ─────────────────────────────────────────────────────────

def make_areas_hub():
    santa_clara = [a for a in AREAS if a["county"] == "Santa Clara"]
    san_mateo = [a for a in AREAS if a["county"] == "San Mateo"]
    def area_cards(areas):
        return "\n".join(f"""
        <a href="/service-areas/{a['slug']}/" class="area-card">
          <h3>{a['name']}</h3>
          <span>{a['county']} County</span>
        </a>""" for a in areas)

    bc, bc_schema = breadcrumbs([("Home", "/"), ("Service Areas", None)])
    content = f"""{head(
        f"Landscaping Service Areas - the South Bay, CA | {NAME}",
        f"{NAME} serves Santa Clara and San Mateo Counties on the South Bay. Click your city to see local landscaping services and get a free estimate.",
        "/service-areas/",
        bc_schema
    )}
{nav(active="areas")}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>the South Bay Landscaping Service Areas</h1>
    <p>{NAME} covers Santa Clara and San Mateo Counties. Select your city for local information and a free estimate.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <h2>Santa Clara County</h2>
    <div class="area-grid">{area_cards(santa_clara)}</div>
    <h2 class="mt-4">San Mateo County</h2>
    <div class="area-grid">{area_cards(san_mateo)}</div>
    <p class="mt-4" style="color:var(--text-mid)">Don't see your city? <a href="tel:{PHONE_RAW}">Call us at {PHONE}</a> - we likely serve your area.</p>
  </div>
</section>
<section class="cta-banner">
  <div class="container">
    <h2>Serving All of the South Bay</h2>
    <p>Call or request online for service in your area.</p>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("service-areas/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: About
# ─────────────────────────────────────────────────────────

def make_about():
    bc, bc_schema = breadcrumbs([("Home", "/"), ("About Us", None)])
    content = f"""{head(
        f"About Us | {NAME} - San Jose, CA",
        f"Learn about {NAME}, the South Bay's landscaping &amp; outdoor renovation company based in {B['city']}, CA. Locally owned, certified, and insured.",
        "/about/",
        bc_schema
    )}
{nav(active="about")}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>About {NAME}</h1>
    <p>the South Bay's locally owned landscaping company - based in {B['city']}, CA.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">Who We Are</span>
      <h2>Built for the South Bay</h2>
    </div>
    <div class="about-content">
      <p>{NAME} is a locally owned landscaping and outdoor renovation company based in San Jose, CA. We serve residential homeowners throughout Santa Clara and San Mateo Counties.</p>
      <p>We're not a national franchise. Every crew member is local, every estimate is honest, and every job is backed by our 100% satisfaction guarantee.</p>
    </div>
    <div class="about-photos">
      <img src="/images/about-us-1.jpg" alt="{NAME} team at work" />
      <img src="/images/about-us-2.jpg" alt="{NAME} landscape project" />
      <img src="/images/about-us-3.jpg" alt="{NAME} outdoor design" />
    </div>
    <ul class="check-list" style="margin-top: 2rem;">
      <li>Fully certified and insured in California</li>
      <li>Locally owned - based in {B['city']}, CA</li>
      <li>Experienced crews with background checks</li>
      <li>100% satisfaction guarantee</li>
      <li>Every project starts with a free on-site consultation</li>
    </ul>
  </div>
</section>
<section class="cta-banner">
  <div class="container">
    <h2>Ready to Work with Us?</h2>
    <p>Call or request a free estimate today.</p>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("about/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: FAQ
# ─────────────────────────────────────────────────────────

def make_faq():
    faq_items = "\n".join(f"""
    <div class="faq-item">
      <button class="faq-question">{f['q']} <span class="faq-icon">+</span></button>
      <div class="faq-answer"><p>{f['a']}</p></div>
    </div>""" for f in FAQS)

    faq_schema_items = json.dumps([{"@type":"Question","name":f["q"],"acceptedAnswer":{"@type":"Answer","text":f["a"]}} for f in FAQS])
    faq_schema = f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":{faq_schema_items}}}</script>'

    bc, bc_schema = breadcrumbs([("Home", "/"), ("FAQ", None)])
    content = f"""{head(
        f"FAQ - Landscaping Questions Answered | {NAME}",
        f"Common questions about {NAME}'s landscaping services in {B['city']}, CA. Get answers about pricing, scheduling, service areas, and more.",
        "/faq/",
        bc_schema + faq_schema
    )}
{nav(active="faq")}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>Frequently Asked Questions</h1>
    <p>Everything you need to know about {NAME}'s services on the South Bay.</p>
  </div>
</section>
<section class="section">
  <div class="container" style="max-width:800px">
    <div class="faq-list">{faq_items}</div>
    <div class="cta-inline mt-4">
      <p>Still have questions? <a href="tel:{PHONE_RAW}">Call or text us at {PHONE}</a> - we respond within 1 business hour.</p>
    </div>
  </div>
</section>
<section class="cta-banner">
  <div class="container">
    <h2>Ready to Get Started?</h2>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("faq/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Reviews
# ─────────────────────────────────────────────────────────

def make_reviews():
    all_reviews = "\n".join(f"""
    <div class="review-card">
      <div class="review-stars">{ICON["star"] * r['rating']}</div>
      <p class="review-text">"{r['text']}"</p>
      <div class="review-author">{r['name']}</div>
      <div class="review-location">{r['location']}</div>
    </div>""" for r in REVIEWS)

    bc, bc_schema = breadcrumbs([("Home", "/"), ("Reviews", None)])
    content = f"""{head(
        f"Customer Reviews | {NAME} - the South Bay, CA",
        f"Read reviews from satisfied customers of {NAME} in {B['city']}, CA and the South Bay. See why we're rated 5 stars.",
        "/reviews/",
        bc_schema
    )}
{nav(active="reviews")}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>Customer Reviews</h1>
    <p>See what the South Bay homeowners and businesses say about {NAME}.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="review-grid">{all_reviews}</div>
    <div class="cta-inline mt-4 text-center">
      <p>Want to leave a review? <a href="https://g.page/r/GOOGLE_REVIEW_LINK/review" target="_blank" rel="noopener">Leave us a Google review →</a></p>
    </div>
  </div>
</section>
<section class="cta-banner">
  <div class="container">
    <h2>Join Our Happy Customers</h2>
    <div class="cta-actions">
      <a href="/request-service.html" class="btn btn-secondary btn-lg">Get Free Estimate</a>
      <a href="tel:{PHONE_RAW}" class="btn btn-outline-white btn-lg">Call {PHONE}</a>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("reviews/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Request Service
# ─────────────────────────────────────────────────────────

def make_request_service():
    bc, bc_schema = breadcrumbs([("Home", "/"), ("Request Service", None)])
    content = f"""{head(
        f"Request a Free Estimate | {NAME} | {PHONE}",
        f"Request a free landscaping estimate from {NAME} in {B['city']}, CA. We serve all of the South Bay and respond within 1 business hour.",
        "/request-service.html",
        bc_schema
    )}
{nav()}
{bc}
<section class="page-hero">
  <div class="container">
    <h1>Request a Free Estimate</h1>
    <p>Fill out the form and we'll get back to you within 1 business hour. No pressure, no obligation.</p>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="content-sidebar-layout">
      <div class="content-main">
        <h2>Let's Talk About Your Project</h2>
        <p>Whether it's a quick lawn mowing quote or a full landscape renovation, we're here to help. Tell us about your project and we'll provide a free, transparent estimate.</p>
        <div class="features-grid" style="margin-top:2rem">
          <div class="feature-card">{ICON["phone_lg"]}<h3>Call or Text</h3><p><a href="tel:{PHONE_RAW}">{PHONE}</a><br/>Mon–Sat, 7am–6pm</p></div>
          <div class="feature-card">{ICON["pin_lg"]}<h3>Our Location</h3><p>{ADDRESS}</p></div>
          <div class="feature-card">{ICON["timer_lg"]}<h3>Response Time</h3><p>Within 1 business hour</p></div>
        </div>
        <div style="margin-top:2rem;border-radius:8px;overflow:hidden">
          <iframe src="{B['googleMapsEmbed']}" width="100%" height="300" style="border:0;display:block" allowfullscreen loading="lazy" title="{NAME} Location Map"></iframe>
        </div>
      </div>
      <aside class="content-sidebar">
        {booking_form()}
      </aside>
    </div>
  </div>
</section>
{footer()}
</body></html>"""
    write("request-service.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Thank You
# ─────────────────────────────────────────────────────────

def make_thank_you():
    content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Request Received | {NAME}</title>
  <meta name="robots" content="noindex" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family={FONT.replace(' ', '+')}:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/css/main.css" />
  <link rel="stylesheet" href="/css/theme.css" />
</head>
<body>
<header class="site-header">
  <nav class="main-nav"><div class="container nav-inner">
    <a href="/" class="nav-logo"><img src="/images/logo.png" alt="{NAME}" height="48" /></a>
    <a href="tel:{PHONE_RAW}" class="nav-phone">{PHONE}</a>
  </div></nav>
</header>

<section class="ty-hero">
  <div class="container ty-hero-inner">
    <div class="ty-check">
      <svg viewBox="0 0 52 52" fill="none" xmlns="http://www.w3.org/2000/svg" width="64" height="64">
        <circle cx="26" cy="26" r="26" fill="var(--green-light)"/>
        <path d="M15 27l8 8 14-16" stroke="#fff" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>
    <h1>Your Request Was Received</h1>
    <p>Thanks for contacting {NAME}. A member of our team will reach out to you within <strong>1 business hour</strong>.</p>
    <a href="tel:{PHONE_RAW}" class="btn btn-primary btn-lg">Call Us Now - {PHONE}</a>
  </div>
</section>

<section class="section section-light">
  <div class="container">
    <div class="section-header">
      <span class="eyebrow">What Happens Next</span>
      <h2>Here's What to Expect</h2>
    </div>
    <div class="steps-grid">
      <div class="step-card">
        <div class="step-number">1</div>
        <h3 class="step-title">We'll Be in Touch</h3>
        <p class="step-desc">Expect a call or text from our team within 1 business hour. We'll confirm your request and answer any questions you have right away.</p>
      </div>
      <div class="step-card">
        <div class="step-number">2</div>
        <h3 class="step-title">Free On-Site Consultation</h3>
        <p class="step-desc">We'll visit your property, walk the space with you, and listen to your vision. No pressure - just an honest conversation about what's possible.</p>
      </div>
      <div class="step-card">
        <div class="step-number">3</div>
        <h3 class="step-title">Your Custom Quote</h3>
        <p class="step-desc">You'll receive a detailed, transparent quote before any work begins. No surprises, no hidden fees - just clear pricing for exactly what you asked for.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container" style="text-align:center;max-width:560px;margin:0 auto">
    <h2>While You Wait</h2>
    <p style="color:var(--gray-mid);margin-bottom:2rem">Browse our services to get inspired, or read what the South Bay homeowners are saying about us.</p>
    <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
      <a href="/services/" class="btn btn-outline">Browse Services</a>
      <a href="/reviews/" class="btn btn-outline">Read Reviews</a>
    </div>
  </div>
</section>

{footer()}
</body></html>"""
    write("thank-you.html", content)


# ─────────────────────────────────────────────────────────
# PAGES: Blog articles
# ─────────────────────────────────────────────────────────

def make_blog_pages():
    posts = [
        {
            "slug": "landscaping-zones",
            "title": "What Landscaping Zone Are You in - and Why Does It Matter?",
            "desc": "Learn about USDA hardiness zones and how to choose plants that thrive on the South Bay. Tips from GreenRidge Landscape & Design in San Jose, CA.",
            "body": f"""
<p>If your plants keep dying or struggling through California weather, hardiness zones might be the answer. the South Bay falls primarily in <strong>USDA Zone 9b-10a</strong> - which means mild winters (as low as 30-40°F) and warm, humid summers. Knowing your zone changes what you plant and when you plant it.</p>
<h2>What Zone Is the South Bay?</h2>
<p>Most of Santa Clara and San Mateo Counties fall in Zone 9b or 10a. The inland areas tend to be slightly warmer; coastal areas and coastal areas are a bit warmer. This matters for anything you're keeping year-round - trees, shrubs, perennials, and ornamental grasses all have zone requirements.</p>
<h2>Best Plants for the South Bay Landscapes</h2>
<ul>
  <li><strong>Ornamental grasses</strong> - drought-tolerant and low-maintenance in Zone 9-10</li>
  <li><strong>Knockout roses</strong> - disease-resistant and reliable in this climate</li>
  <li><strong>Boxwood</strong> - classic hedge material that handles California weather well</li>
  <li><strong>Japanese maples</strong> - thrive in Zone 9-10, stunning fall color</li>
  <li><strong>Blue Star juniper</strong> - evergreen, low-maintenance, great for borders</li>
</ul>
<h2>What Our Team Recommends</h2>
<p>At {NAME}, every landscape design starts with a site visit where we assess your soil, sun exposure, drainage, and existing plantings. We only recommend plants we know will thrive on the South Bay - not whatever looks good at a nursery in the moment.</p>
<p>Want a plant selection that will actually last? <a href="/request-service.html">Request a free consultation</a> and we'll walk your property and give you honest recommendations.</p>"""
        },
        {
            "slug": "outdoor-landscaping-ideas",
            "title": "Outdoor Landscaping Ideas for Every Budget",
            "desc": "Creative outdoor renovation ideas for the South Bay homeowners - from patio builds to full landscape transformations. Tips from GreenRidge Landscape & Design.",
            "body": f"""
<p>You don't need to spend a fortune to dramatically improve your outdoor space. Here are ideas across every budget range - from simple weekend projects to full outdoor renovations.</p>
<h2>Under $2,000 - Quick Impact</h2>
<ul>
  <li><strong>Define your garden beds</strong> - fresh mulch and clean edge lines transform the look of any yard instantly</li>
  <li><strong>Add a focal point</strong> - a single ornamental tree, a decorative boulder, or a simple planting cluster draws the eye and anchors the space</li>
  <li><strong>Upgrade your walkway edging</strong> - simple steel or stone edging along a path adds structure without major cost</li>
</ul>
<h2>$2,000–$10,000 - Real Transformation</h2>
<ul>
  <li><strong>Paver patio</strong> - a modest 200–300 sq ft patio adds usable outdoor living space and significant property value</li>
  <li><strong>Front yard redesign</strong> - new plantings, bed design, and lawn restoration can completely change your curb appeal</li>
  <li><strong>Privacy plantings</strong> - a row of arborvitae or holly creates a natural privacy screen that improves with age</li>
</ul>
<h2>$10,000+ - Full Outdoor Renovation</h2>
<ul>
  <li><strong>Complete back yard overhaul</strong> - patio, garden beds, lawn restoration, and plantings as a cohesive design</li>
  <li><strong>Outdoor living environment</strong> - pergola, fire feature, outdoor kitchen, and entertaining space</li>
  <li><strong>Paver driveway</strong> - one of the highest ROI upgrades for the South Bay homes</li>
</ul>
<p>Not sure what fits your budget and property? {NAME} offers free on-site consultations where we can help you prioritize and plan. <a href="/request-service.html">Book yours today.</a></p>"""
        },
        {
            "slug": "spring-lawn-tuneup",
            "title": "Why You Should Schedule a Spring Tune-Up for Your Landscape",
            "desc": "Spring is the best time to set your the South Bay landscape up for the season. Here's what a professional spring tune-up includes and why it matters.",
            "body": f"""
<p>Winter on the South Bay is tough on landscapes. Frost heaving, salt spray from roads, compacted soil, and dormant damage all add up. A professional spring tune-up addresses all of it before the growing season starts - and the difference shows all year.</p>
<h2>What a Spring Landscape Tune-Up Includes</h2>
<ul>
  <li><strong>Cleanup</strong> - removal of winter debris, dead material, and fallen branches</li>
  <li><strong>Bed edging and reshaping</strong> - clean lines define the space and prepare beds for new growth</li>
  <li><strong>Mulch application</strong> - fresh mulch retains moisture, suppresses weeds, and gives beds a finished look</li>
  <li><strong>Pruning</strong> - late-winter pruning of ornamentals and shrubs promotes healthy growth and shape</li>
  <li><strong>Lawn assessment</strong> - identify bare or damaged spots early and address them before summer heat sets in</li>
</ul>
<h2>Why Timing Matters</h2>
<p>The window for effective spring prep on the South Bay is roughly <strong>late March through early May</strong>. Too early and the ground is still frozen; too late and fast-growing weeds get ahead of you. Getting on the schedule early means your property looks great from the first warm weekend.</p>
<h2>Book Before the Rush</h2>
<p>Spring is our busiest season. If you want to get on the schedule, reach out in late winter - spots fill up fast. <a href="/request-service.html">Request a free estimate</a> and we'll assess your property and put together a spring plan.</p>"""
        }
    ]
    for post in posts:
        bc, bc_schema = breadcrumbs([("Home", "/"), ("Resources", None), (post["title"][:40] + "…", None)])
        content = f"""{head(
            f"{post['title']} | {NAME}",
            post["desc"],
            f"/blog/{post['slug']}/",
            bc_schema
        )}
{nav()}{bc}
<section class="page-hero">
  <div class="container">
    <h1>{post['title']}</h1>
  </div>
</section>
<section class="section">
  <div class="container blog-post-layout">
    <article class="blog-post-body">
      {post['body']}
      <div class="blog-post-cta">
        <h3>Ready to Transform Your Outdoor Space?</h3>
        <p>{NAME} serves all of the South Bay - San Jose and the South Bay Area. Free estimates, no obligation.</p>
        <a href="/request-service.html" class="btn btn-primary">Get a Free Estimate</a>
      </div>
    </article>
    <aside class="blog-post-sidebar">
      <div class="booking-card">
        <div class="booking-card-header">
          <h3>Free Estimate</h3>
          <p>Response within 1 business hour</p>
        </div>
        <div style="padding:20px">
          <p style="font-size:.9rem;color:var(--gray-dark);margin-bottom:16px">Ready to get started? Call or text us and we'll schedule a free on-site consultation.</p>
          <a href="tel:{PHONE_RAW}" class="btn btn-primary btn-block">Call {PHONE}</a>
          <a href="/request-service.html" class="btn btn-outline btn-block" style="margin-top:10px">Request Online</a>
        </div>
      </div>
      <div class="sidebar-services">
        <h4>Our Services</h4>
        <ul>{"".join(f'<li><a href="/services/{s["slug"]}/">{s["name"]}</a></li>' for s in SERVICES)}</ul>
      </div>
    </aside>
  </div>
</section>
{footer()}
</body></html>"""
        write(f"blog/{post['slug']}/index.html", content)


# ─────────────────────────────────────────────────────────
# PAGE: Privacy Policy & Terms (boilerplate)
# ─────────────────────────────────────────────────────────

def make_legal():
    for slug, title, body in [
        ("privacy-policy", "Privacy Policy", f"<p>{NAME} respects your privacy. We collect contact information submitted through our forms solely to respond to your service inquiry. We do not sell or share your information with third parties. For questions, call {PHONE}.</p>"),
        ("terms", "Terms of Use", f"<p>By using this website, you agree to these terms of use. All content on this site is owned by {NAME}. Unauthorized reproduction is prohibited. For questions, contact us at {PHONE}.</p>"),
        ("accessibility", "Accessibility", f"<p>{NAME} is committed to ensuring this website is accessible to people with disabilities. If you experience any difficulty, please call us at {PHONE} and we will assist you.</p>"),
    ]:
        bc, bc_schema = breadcrumbs([("Home", "/"), (title, None)])
        content = f"""{head(f"{title} | {NAME}", f"{title} for {NAME}, {B['city']}, CA.", f"/{slug}.html", bc_schema)}
{nav()}{bc}
<section class="page-hero"><div class="container"><h1>{title}</h1></div></section>
<section class="section"><div class="container" style="max-width:800px">{body}</div></section>
{footer()}</body></html>"""
        write(f"{slug}.html", content)


# ─────────────────────────────────────────────────────────
# RUN ALL GENERATORS
# ─────────────────────────────────────────────────────────

print(f"Generating {NAME} site...\n")

make_theme_css()
make_homepage()
make_services_hub()
for s in SERVICES:
    make_service_page(s)
make_areas_hub()
for a in AREAS:
    make_city_page(a)
make_about()
make_faq()
make_reviews()
make_request_service()
make_thank_you()
make_blog_pages()
make_legal()

print(f"[OK] {len(pages_created)} pages generated:\n")
for p in sorted(pages_created):
    print(f"   {p}")

if pages_failed:
    print(f"\n[FAIL] {len(pages_failed)} failed:")
    for p in pages_failed:
        print(f"   {p}")

print(f"\nTotal: {len(pages_created)} pages")
