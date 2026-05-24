# Site Factory Design

**Date:** 2026-04-20
**Author:** Isayah Young-Burke (Zay)
**Status:** Approved

## Goal

Use Green Empire as a master template to spin up identical-looking websites for new local business clients. Give the client's branding and content as inputs, get a fully working site as output — within one week of receiving complete client info.

## Architecture

Green Empire (`green-empire-template`) becomes the master template repo and is never modified for client work. Each new client gets their own GitHub repo cloned from it.

```
green-empire-template/   ← master template (source of truth)
ariel-handyman/          ← client repo (cloned + configured)
client-3/                ← next client, same pattern
```

## The Generator Script

A Node.js script (`generate.js`) lives in the template repo. It reads `site.config.json` and rebuilds all HTML pages with the client's brand, services, cities, reviews, and FAQs.

**Workflow per new client:**
1. Clone `green-empire-template` into a new repo named after the client
2. Fill out `site.config.json` with client info received via onboarding email
3. Run `node generate.js` — all HTML pages regenerate
4. Review, push to GitHub, deploy to VM

The script is run once at setup and again any time the client requests content changes.

## site.config.json — What Changes Per Client

All client-specific content lives here. Nothing else needs to be touched.

| Field | Description |
|---|---|
| `business.name` | Exact business name |
| `business.tagline` | One-line description |
| `business.phone` | Display + tel: href phone number |
| `business.email` | Contact email address |
| `business.address` | Address or service region |
| `business.hours` | Hours of operation |
| `brand.primaryColor` | Hex code |
| `brand.secondaryColor` | Hex code |
| `brand.font` | Google Font name |
| `brand.logo` | Path to logo file |
| `services[]` | Name, description, icon per service |
| `cities[]` | List of service area cities/towns |
| `reviews[]` | Name, rating, text per review |
| `faqs[]` | Question + answer pairs |
| `hero.heading` | Main hero headline |
| `hero.subheading` | Hero supporting text |
| `hero.image` | Path to hero background image |
| `zapier.webhookUrl` | Client-specific Zapier webhook URL |
| `forms.notifyEmail` | Email address to receive leads |
| `forms.notifyPhone` | Phone number to receive SMS on form submit |

## What Stays the Same Across All Sites

- HTML/CSS/JS structure and file layout
- Lucide icons (CDN)
- Mobile nav, FAQ accordion, async form submit logic
- Page types: home, services, cities, about, contact, booking
- nginx deployment flow
- Vanilla HTML — no frontend frameworks

## Forms & Zapier

One Zapier account managed by Zay. Each client site gets its own webhook URL (separate Zap). When a lead form is submitted, Zapier routes it to that client's email and phone number.

**Per-client Zap setup:**
- Trigger: Catch Hook → unique webhook URL
- Action 1: Gmail → send to client's `notifyEmail`
- Action 2: SMS → send to client's `notifyPhone`
- Form fields: name, phone, service, message, sms_opt_in

**Future:** Migrate to self-hosted N8N once there are 3+ active client sites to avoid Zapier per-task costs.

## Deployment

Same flow as Green Empire:
1. Push to client's GitHub repo
2. SSH into VM
3. `git pull origin master`

nginx on the VM handles multiple domains. Each client site is a separate nginx server block pointing to its own directory. New clients can be added to the same VM or a new one spun up as needed.

## Client Onboarding Email

Before any build starts, send the client the requirements email. The one-week build clock starts when **all** info is received — not when the email is sent.

**Required inputs:**
- Business name, type, tagline
- Phone, email, address, hours
- Logo (PNG, transparent background)
- Brand colors and font preference
- Services list with descriptions
- Service area cities/towns
- 3-5 real customer reviews
- Hero photo and any job photos
- About section (2-3 sentences)
- 3-5 FAQs
- Form notification email and phone number
- Domain name (or budget to register one ~$15)

## Timeline

| Day | Task |
|---|---|
| Day 0 | Receive complete client info |
| Day 1 | Clone template, fill site.config.json, run generator |
| Day 2 | Review output, swap in real photos, fine-tune CSS |
| Day 3 | Set up Zapier webhook, test form end-to-end |
| Day 4 | DNS setup, deploy to VM, smoke test all pages |
| Day 5 | Client review, revisions |
| Day 6-7 | Buffer for changes and sign-off |

## Out of Scope

- CMS or client self-service editing
- Custom page types beyond the Green Empire page set
- E-commerce or payment processing
- SEO automation (meta tags are set manually per site)
