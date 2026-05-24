# CLAUDE.md - Green Empire Landscaping

## Project Overview
Client website for Green Empire Landscaping, a landscaping business in Long Island, NY.

**Domain:** https://greenempireland.com
**Port:** 3019 (Docker container)
**Admin:** Managed via zaylegend.com/admin

---

## Pending Tasks

### Photo Replacement (Priority)
The site currently uses repeated placeholder images. The following need unique photos:

**Homepage (`index.html`) - Most duplicates:**
| Current Image | Section | Replace With |
|---------------|---------|--------------|
| `xrda4x...png` | Used 3x | Needs 2 unique alternatives |
| `i4xd76...png` | Used 2x | Needs 1 unique alternative |
| `7vpm8z...png` | Used 2x | Needs 1 unique alternative |
| `5uib28...png` | Used 2x | Needs 1 unique alternative |
| `imgt0p...png` | Used 2x | Needs 1 unique alternative |

**Services page (`services/index.html`):**
- Uses same images as homepage
- Each service card should have a unique, relevant photo

**Images directory:** `/var/www/Green-Empire/images/`

### After Adding Photos
1. Update the HTML files with new image paths
2. Rebuild Docker: `cd /var/www/Green-Empire && docker build -t green-empire . && docker stop green-empire && docker rm green-empire && docker run -d --name green-empire -p 3019:80 green-empire`

---

## Recent Changes (2026-04-11)
- Updated canonical URLs from greenempirelandscaping.com → greenempireland.com
- Fixed logo size (120px → 64px) to prevent menu overlay
- Set up SSL via Let's Encrypt
- Configured nginx for standalone domain

---

## Git Status
- Local commit ready, needs push to GitHub
- Remote: git@github.com:yetog/Green-Empire.git
- Note: Deploy key needs write access to push

---

## Tech Stack
- Static HTML/CSS site
- Served via nginx:alpine Docker container
- No build step required - just edit HTML and rebuild container
