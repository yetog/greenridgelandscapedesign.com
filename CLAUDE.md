# GreenRidge Landscape & Design - Website Documentation

> Static website for GreenRidge Landscape & Design, a San Jose landscaping company.
> Created: 2026-05-24

---

## Quick Reference

| Item | Value |
|------|-------|
| **Live URL** | https://greenridgelandscapedesign.com |
| **Client** | Ariel (GreenRidge Landscape & Design) |
| **Location** | San Jose, CA |
| **Phone** | (408) 512-3074 |
| **Email** | greenridgelandscapers@gmail.com |
| **Server Path** | `/var/www/greenridgelandscapedesign/` |
| **Nginx Config** | `/etc/nginx/conf.d/greenridgelandscapedesign.conf` |
| **SSL Cert** | `/etc/letsencrypt/live/greenridgelandscapedesign.com/` |
| **GitHub Repo** | `git@github.com:yetog/greenridgelandscapedesign.com.git` |

---

## Tech Stack

- **Type**: Static HTML site
- **Generator**: Python (`generate.py`)
- **Config**: `site.config.json`
- **Styling**: Custom CSS with CSS variables
- **Server**: Nginx with SSL (Let's Encrypt)
- **Based on**: Green Empire Landscaping template

---

## Brand Guidelines

### Colors
| Color | Hex | Usage |
|-------|-----|-------|
| Primary Green | `#2C4A1E` | Accent color, headers, footer |
| Cream | `#F5F0E8` | Main background (light/airy feel) |
| Warm Stone | `#C8B89A` | Buttons, CTAs, accents |
| Charcoal | `#1A1A1A` | Text only |

### Style
- Light and airy California luxury outdoor living vibe
- Less dark/heavy contractor feeling
- Softer overlays on hero images
- Clean spacing and modern luxury feel

---

## Site Structure

```
/var/www/greenridgelandscapedesign/
├── index.html                 # Homepage
├── site.config.json           # All content configuration
├── generate.py                # Site generator script
├── css/
│   ├── main.css               # Primary styles
│   ├── theme.css              # Auto-generated color variables
│   └── footer.css             # Footer styles
├── images/                    # Optimized images (JPG, 150-330KB each)
├── services/                  # 7 service pages
├── service-areas/             # 15 South Bay area pages
├── about/                     # About page
├── faq/                       # FAQ page
├── reviews/                   # Reviews page
├── blog/                      # Blog posts
├── request-service.html       # Contact form
└── thank-you.html             # Form confirmation
```

---

## Services (7)

1. Landscape Design & Installation
2. Paver Installation
3. Patio Installation
4. Driveway Installation
5. Front Yard Landscaping
6. Back Yard Landscaping
7. Outdoor Living Spaces

---

## Service Areas (15)

San Jose, Santa Clara, Sunnyvale, Cupertino, Campbell, Los Gatos, Saratoga, Milpitas, Mountain View, Palo Alto, Fremont, Morgan Hill, Los Altos, Menlo Park, Redwood City

---

## Common Tasks

### Regenerate Site
```bash
cd /var/www/greenridgelandscapedesign
python3 generate.py
```

### Edit Content
1. Edit `site.config.json`
2. Run `python3 generate.py`

### Add New Service
1. Add to `services` array in `site.config.json`
2. Regenerate site

### Add New Service Area
1. Add to `serviceAreas` array in `site.config.json`
2. Regenerate site

### Optimize New Images
```bash
cd /var/www/greenridgelandscapedesign/images
convert input.png -resize "1200x1200>" -quality 85 output.jpg
```

### Reload Nginx
```bash
sudo nginx -t && sudo nginx -s reload
```

---

## SSL Certificate

- Provider: Let's Encrypt
- Auto-renewal: Enabled via certbot
- Expires: 2026-08-22
- Domains: greenridgelandscapedesign.com, www.greenridgelandscapedesign.com

---

## Image Optimization

All images optimized for web:
- Format: JPG (was PNG)
- Max dimensions: 1200x1200 or 1920x1080 (hero)
- Quality: 80-85%
- Size: 150-330KB each (was 3-11MB)

---

## Forms

Contact form submits to:
- Email: greenridgelandscapers@gmail.com
- SMS: 5167121231

---

## Deployment Notes

### Initial Setup (Completed 2026-05-24)
1. Cloned Green Empire template
2. Updated site.config.json with GreenRidge info
3. Updated CSS for California luxury style (cream background, warm stone accents)
4. Optimized images (170MB -> 3MB)
5. Cleaned up copy (removed em dashes, Long Island references)
6. Set up SSL with certbot
7. Configured www -> non-www redirect

### Pending
- [ ] Set up GitHub deploy key for pushing from server
- [ ] Clean git history to remove large PNG files

---

## Related Projects

- Green Empire Landscaping (greenempireland.com) - Same template
- Template source: `/var/www/Green-Empire/`

---

## Contact

**Client:** Ariel
**Business:** GreenRidge Landscape & Design
**Address:** 2557 Bergman Ct, San Jose, CA 95121
**Phone:** (408) 512-3074
**Email:** greenridgelandscapers@gmail.com
**Hours:** Mon-Sat 8:00 AM - 6:00 PM
