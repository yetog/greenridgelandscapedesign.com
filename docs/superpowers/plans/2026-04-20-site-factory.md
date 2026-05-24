# Site Factory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Green Empire codebase a true config-driven template so any new client site can be launched by filling out `site.config.json` and running `python generate.py`.

**Architecture:** Four targeted fixes to the existing generator: (1) move the Zapier webhook URL into config, (2) have the generator produce a `css/theme.css` that injects brand colors so `main.css` stays untouched, (3) fix the hardcoded phone number in the JS form error handler, (4) add a quick-start README. No new frameworks, no structural changes.

**Tech Stack:** Python 3, JSON, vanilla HTML/CSS/JS, Zapier webhooks

---

## File Map

| File | Change |
|---|---|
| `site.config.json` | Add `zapierWebhook`, `font`, `forms.notifyEmail`, `forms.notifyPhone`; remove `formspreeId` |
| `generate.py` | Use `zapierWebhook` in form action; generate `css/theme.css`; inject `data-phone` on forms |
| `css/theme.css` | New generated file — CSS custom property overrides per client |
| `css/main.css` | Remove hardcoded color comments; switch `:root` vars to use theme.css values |
| `js/main.js` | Read phone from `form.dataset.phone` instead of hardcoded string |
| `README.md` | New — quick-start guide for launching a new client site |

---

## Task 1: Update site.config.json schema

**Files:**
- Modify: `site.config.json`

- [ ] **Step 1: Replace `formspreeId` with `zapierWebhook` and add new fields**

Open `site.config.json` and make these changes to the `brand` object:

Remove:
```json
"formspreeId": "xdapbeoj",
```

Add (keep everything else, insert after `googleMapsEmbed`):
```json
"zapierWebhook": "https://hooks.zapier.com/hooks/catch/26765756/u7mrips/",
"font": "Inter",
"forms": {
  "notifyEmail": "greenempireland@gmail.com",
  "notifyPhone": "5163214243196"
},
```

Final `brand` block order: name, tagline, phone, phoneRaw, email, address, city, state, zip, hours, domain, zapierWebhook, font, forms, facebook, instagram, googleMapsEmbed, primaryColor, primaryDark, secondaryColor, secondaryDark, industry, industryLower

- [ ] **Step 2: Verify JSON is valid**

```bash
python3 -c "import json; json.load(open('site.config.json')); print('valid')"
```

Expected: `valid`

- [ ] **Step 3: Commit**

```bash
git add site.config.json
git commit -m "config: add zapierWebhook, font, forms fields; remove formspreeId"
```

---

## Task 2: Fix form action URL in generate.py

**Files:**
- Modify: `generate.py:14-26` (config extraction block)
- Modify: `generate.py:195-220` (booking_form function)

- [ ] **Step 1: Write a test that will fail**

Create `tests/test_generator.py`:

```python
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def load_cfg():
    with open("site.config.json") as f:
        return json.load(f)

def test_form_action_uses_zapier():
    cfg = load_cfg()
    webhook = cfg["brand"]["zapierWebhook"]
    assert "zapier" in webhook, "zapierWebhook not in config"
    # Import the generated HTML for index.html and check form action
    with open("index.html") as f:
        html = f.read()
    assert f'action="{webhook}"' in html, f"Form action should be {webhook}"

def test_no_formspree_in_generated_pages():
    with open("index.html") as f:
        html = f.read()
    assert "formspree" not in html, "Formspree URL found in generated page"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python3 -m pytest tests/test_generator.py::test_form_action_uses_zapier -v
```

Expected: FAIL — `formspree` is in form action, not zapier

- [ ] **Step 3: Update the config extraction block in generate.py**

At the top of `generate.py`, after line 26 (where `SECONDARY` is set), add:

```python
WEBHOOK = B["zapierWebhook"]
FONT    = B.get("font", "Inter")
```

- [ ] **Step 4: Update both booking_form variants in generate.py**

Find both occurrences of:
```python
<form action="https://formspree.io/f/{B['formspreeId']}" method="POST" class="booking-form">
```

Replace both with:
```python
<form action="{WEBHOOK}" method="POST" class="booking-form" data-phone="{PHONE}">
```

Note: `data-phone` is added here — it will be used in Task 4.

- [ ] **Step 5: Run the generator**

```bash
python3 generate.py
```

Expected: output listing all generated pages, no errors

- [ ] **Step 6: Run the test**

```bash
python3 -m pytest tests/test_generator.py::test_form_action_uses_zapier tests/test_generator.py::test_no_formspree_in_generated_pages -v
```

Expected: both PASS

- [ ] **Step 7: Commit**

```bash
git add generate.py tests/test_generator.py
git commit -m "fix: use zapierWebhook from config for all form actions"
```

---

## Task 3: Generate CSS theme file for brand colors

**Files:**
- Modify: `generate.py` — add `make_theme_css()` function and call it in main
- Create: `css/theme.css` (generated output, not hand-edited)
- Modify: `css/main.css` — remove hardcoded color values from `:root`

The problem: `css/main.css` has `--green: #1e4d2b` etc. hardcoded. Changing a client's brand color currently requires manually editing CSS. The fix: the generator writes `css/theme.css` with the client's colors, and `main.css` imports it.

- [ ] **Step 1: Write a failing test**

Add to `tests/test_generator.py`:

```python
def test_theme_css_exists():
    assert os.path.exists("css/theme.css"), "css/theme.css not generated"

def test_theme_css_contains_brand_colors():
    cfg = load_cfg()
    primary = cfg["brand"]["primaryColor"]
    secondary = cfg["brand"]["secondaryColor"]
    with open("css/theme.css") as f:
        css = f.read()
    assert primary in css, f"Primary color {primary} not in theme.css"
    assert secondary in css, f"Secondary color {secondary} not in theme.css"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python3 -m pytest tests/test_generator.py::test_theme_css_exists tests/test_generator.py::test_theme_css_contains_brand_colors -v
```

Expected: both FAIL — `css/theme.css` does not exist

- [ ] **Step 3: Add make_theme_css() to generate.py**

Add this function after the `FONT` variable line:

```python
def make_theme_css():
    primary_dark  = B.get("primaryDark", B["primaryColor"])
    secondary_dark = B.get("secondaryDark", B["secondaryColor"])
    content = f"""/* Auto-generated by generate.py — do not edit manually */
:root {{
  --green:        {B["primaryColor"]};
  --green-dark:   {primary_dark};
  --green-light:  {B["secondaryColor"]};
  --green-hover:  {secondary_dark};
}}
"""
    write("css/theme.css", content)
```

- [ ] **Step 4: Call make_theme_css() in the main block**

Find the section at the bottom of `generate.py` where page generators are called (e.g. `make_homepage()`, `make_service_page(s)`, etc.). Add `make_theme_css()` as the first call:

```python
make_theme_css()
make_homepage()
# ... rest of calls unchanged
```

- [ ] **Step 5: Add theme.css link to the head() function in generate.py**

Find the `head()` function. Locate the line that links `main.css`:
```python
<link rel="stylesheet" href="/css/main.css">
```

Add `theme.css` directly after it:
```python
<link rel="stylesheet" href="/css/main.css">
<link rel="stylesheet" href="/css/theme.css">
```

- [ ] **Step 6: Remove the hardcoded color vars from main.css**

In `css/main.css`, find the `:root` block that contains `--green`, `--green-dark`, `--green-light`, `--green-hover`. Remove only those four lines — leave all other `:root` variables untouched:

```css
/* remove these four lines: */
--green:        #1e4d2b;
--green-dark:   #153820;
--green-light:  #6aad32;
--green-hover:  #5a9e2f;
```

- [ ] **Step 7: Run the generator**

```bash
python3 generate.py
```

Expected: no errors, `css/theme.css` created

- [ ] **Step 8: Run all tests**

```bash
python3 -m pytest tests/test_generator.py -v
```

Expected: all PASS

- [ ] **Step 9: Smoke test in browser**

Open `index.html` in a browser. Verify the green color scheme still renders correctly (buttons, header, accents).

- [ ] **Step 10: Commit**

```bash
git add generate.py css/main.css css/theme.css tests/test_generator.py
git commit -m "feat: generate css/theme.css with brand colors from config"
```

---

## Task 4: Fix hardcoded phone number in form error handler

**Files:**
- Modify: `js/main.js` — read phone from `form.dataset.phone`

The form error message in `main.js` has the phone hardcoded:
```javascript
btn.textContent = 'Error — call us at (516) 774-2956';
```
This needs to come from the form's `data-phone` attribute (set in Task 2).

- [ ] **Step 1: Write a failing test**

Add to `tests/test_generator.py`:

```python
def test_main_js_has_no_hardcoded_phone():
    cfg = load_cfg()
    phone = cfg["brand"]["phone"]
    with open("js/main.js") as f:
        js = f.read()
    assert phone not in js, f"Hardcoded phone {phone} found in main.js — should use data-phone attribute"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python3 -m pytest tests/test_generator.py::test_main_js_has_no_hardcoded_phone -v
```

Expected: FAIL — phone number is hardcoded in main.js

- [ ] **Step 3: Update main.js**

Find this block in `js/main.js`:

```javascript
    } catch {
      btn.textContent = 'Error — call us at (516) 774-2956';
      btn.style.background = '#dc2626';
```

Replace with:

```javascript
    } catch {
      const phone = form.dataset.phone || '';
      btn.textContent = phone ? `Error — call us at ${phone}` : 'Error sending — please call us';
      btn.style.background = '#dc2626';
```

- [ ] **Step 4: Run all tests**

```bash
python3 -m pytest tests/test_generator.py -v
```

Expected: all PASS

- [ ] **Step 5: Run the generator and verify data-phone in output**

```bash
python3 generate.py
grep -o 'data-phone="[^"]*"' index.html
```

Expected: `data-phone="(516) 774-2956"`

- [ ] **Step 6: Commit**

```bash
git add js/main.js
git commit -m "fix: read error phone number from form data-phone attribute"
```

---

## Task 5: Add quick-start README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README.md**

```markdown
# Site Factory — Quick Start

This repo is a config-driven static site template. To launch a new client site:

## 1. Clone this repo

```bash
git clone https://github.com/yetog/Green-Empire new-client-name
cd new-client-name
git remote set-url origin https://github.com/your-org/new-client-name
```

## 2. Fill out site.config.json

Update every field in the `brand` object with the client's info. Key fields:

| Field | Description |
|---|---|
| `name` | Business name |
| `tagline` | One-line description |
| `phone` / `phoneRaw` | Display phone and digits-only version |
| `email` | Contact email |
| `address`, `city`, `state`, `zip` | Business location |
| `hours` | Hours of operation |
| `zapierWebhook` | Zapier webhook URL for form submissions |
| `font` | Google Font name (default: "Inter") |
| `forms.notifyEmail` | Email to receive lead notifications |
| `forms.notifyPhone` | Phone to receive SMS notifications |
| `primaryColor` / `primaryDark` | Brand primary hex colors |
| `secondaryColor` / `secondaryDark` | Brand secondary hex colors |
| `facebook` / `instagram` | Social links |

Then update `services`, `serviceAreas`, `reviews`, `faqs`, and `gallery` arrays for the client.

## 3. Replace images

Drop client assets into `/images/`:
- `logo.png` — PNG with transparent background
- `hero-bg.jpg` — hero background image
- Job photos for gallery and service pages

## 4. Run the generator

```bash
python3 generate.py
```

This regenerates all HTML pages and `css/theme.css` from your config.

## 5. Set up Zapier

1. Go to zapier.com → Create Zap
2. Trigger: Webhooks by Zapier → Catch Hook
3. Copy the webhook URL into `site.config.json` → `brand.zapierWebhook`
4. Action 1: Gmail → Send Email to `forms.notifyEmail`
5. Action 2: SMS (via Twilio or similar) → Send to `forms.notifyPhone`
6. Re-run `python3 generate.py` after updating the webhook URL

## 6. Deploy

```bash
git add -A
git commit -m "init: [client name] site"
git push origin master
# SSH into VM and pull
ssh user@yourserver 'cd /var/www/client-name && git pull origin master'
```

## Page types generated

- Homepage (`index.html`)
- Services hub (`/services/`)
- One page per service (`/services/[slug]/`)
- Service areas hub (`/service-areas/`)
- One page per city (`/service-areas/[slug]/`)
- About, Reviews, FAQ pages
- Request service form (`/request-service.html`)
- Thank you page (`/thank-you.html`)
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add quick-start README for site factory workflow"
```

---

## Task 6: Final verification

- [ ] **Step 1: Run full test suite**

```bash
python3 -m pytest tests/ -v
```

Expected: all tests PASS

- [ ] **Step 2: Run the generator clean**

```bash
python3 generate.py
```

Expected: no errors, reports all pages created

- [ ] **Step 3: Spot-check key pages**

Open in browser and verify:
- `index.html` — correct phone, correct colors, form action is Zapier URL
- `services/back-yard-landscaping/index.html` — form action is Zapier URL, data-phone set
- `css/theme.css` — contains `#1e4d2b` and `#6aad32`

- [ ] **Step 4: Push to GitHub**

```bash
git push origin master
```

- [ ] **Step 5: Mark repo as GitHub template (manual)**

Go to GitHub repo settings → check "Template repository". Future clients: click "Use this template" to get a clean clone.
