# Parent Recall Watch - Setup Guide

## Quick Start (5 minutes)

### 1. Create GitHub Repo
```bash
cd cpsc-recall-tracker
git init
git add -A
git commit -m "Initial commit - CPSC Recall Tracker"
gh repo create newparentreviews-recalls --private --source=. --push
```

### 2. Connect to Netlify
- Go to Netlify Dashboard > New Site > Import from Git
- Select the `newparentreviews-recalls` repo
- Build settings: leave blank (we push pre-built files)
- Deploy!

### 3. Set Up as Subdirectory of newparentreviews.net
In your main newparentreviews.net Netlify config, add a proxy redirect:
```toml
[[redirects]]
  from = "/recalls/*"
  to = "https://YOUR-RECALL-SITE.netlify.app/:splat"
  status = 200
```
Or: configure the recalls repo as a separate Netlify site with custom domain `newparentreviews.net` and base path `/recalls/`.

### 4. IMPORTANT: Configure Your Accounts

**Amazon Affiliate Tag:**
Open `scripts/generate_site.py` and replace:
```python
AMAZON_TAG = "newparentrev-20"
```
with your actual Amazon Associates tag.

**Beehiiv Newsletter:**
1. Create a free Beehiiv account at beehiiv.com
2. Create a publication
3. Get your publication ID from Settings > Integrations > API
4. Open `scripts/generate_site.py` and replace:
```python
BEEHIIV_PUBLICATION_ID = "YOUR_BEEHIIV_PUB_ID"
```

**Cross-links to NewParentReviews.net:**
Update the `CROSS_LINKS` dict in `generate_site.py` to match your actual review page URLs:
```python
CROSS_LINKS = {
    "cribs-cradles": "/your-actual-crib-review-page",
    "strollers": "/your-actual-stroller-review-page",
    ...
}
```

### 5. First Real Data Pull
```bash
# Full historical pull (5 years of recalls)
python scripts/fetch_recalls.py full

# Regenerate site with real data
python scripts/generate_site.py

# Commit and push
git add -A
git commit -m "Seed with 5 years of CPSC recall data"
git push
```

### 6. Enable Daily Automation
The GitHub Action (`.github/workflows/daily-update.yml`) runs automatically every day at 6 AM UTC.
- Fetches new recalls from the last 60 days
- Regenerates ALL pages (recall details, categories, brands, lookup tool, sitemap)
- Commits and pushes if there are changes
- Netlify auto-deploys on push

**Optional:** Add a Netlify Build Hook for instant deploys:
1. Netlify > Site > Build hooks > Add build hook
2. Copy the URL
3. GitHub > Repo Settings > Secrets > Add `NETLIFY_BUILD_HOOK`
4. Uncomment the `notify-netlify` job in the workflow file

## File Structure
```
cpsc-recall-tracker/
├── .github/workflows/daily-update.yml  # Daily cron automation
├── scripts/
│   ├── fetch_recalls.py                # CPSC API fetcher
│   ├── generate_site.py                # Static site generator (v2 with monetization)
│   └── seed_sample_data.py             # Sample data for testing
├── data/
│   └── recalls.json                    # Raw recall data (auto-generated)
├── assets/css/style.css                # All styles
├── categories/                          # Category listing pages
├── brands/                              # Brand index pages (Graco, Fisher-Price, etc.)
├── check/                               # "Is My Product Recalled?" lookup tool
├── recall/                              # Individual recall detail pages
├── index.html                           # Homepage
├── all-recalls.html                     # Full recall listing
├── sitemap.xml                          # Auto-generated sitemap
├── robots.txt                           # SEO
└── netlify.toml                         # Netlify config
```

## Revenue Streams (All Built In)

### 1. Amazon Affiliate Links (Active)
Every recall detail page has a "Need a Safe Replacement?" box with Amazon search links using your affiliate tag. Category pages also have them. These are highest-intent clicks - parents whose product just got recalled are buying a replacement TODAY.

### 2. Beehiiv Email Newsletter (Active)
Email capture form on every page. Hook up to Beehiiv (free up to 2,500 subs). Send alerts when new recalls drop. Include affiliate links in emails. Open rates on safety alerts are extremely high.

### 3. Cross-links to NewParentReviews.net (Active)
Recall pages link to your review pages ("Read our Car Seat reviews on NewParentReviews"). Review pages should link back ("Check recall status"). This passes SEO authority both ways.

### 4. "Is My Product Recalled?" Lookup Tool
High-value utility page that earns backlinks from parenting forums and Facebook groups. Built-in client-side search across all recalls. Also shows affiliate links.

### 5. Brand Pages for SEO
One page per brand (Graco, Britax, IKEA, etc.) showing all their recalls. Targets "[brand] recalls" searches. Auto-generated from data.

### 6. Display Ads (Future)
Once you hit 10k-50k monthly sessions, apply for Mediavine or Raptive. The clean layout has plenty of space for ad placements.

## SEO Strategy
- Recall detail pages target: "[Brand] [Product] recall" (e.g., "Graco stroller recall")
- Category pages target: "[Category] recalls" (e.g., "car seat recalls 2025")
- Brand pages target: "[Brand] recalls" (e.g., "Fisher-Price recalls")
- Check tool targets: "is my [product] recalled", "product recall checker"
- Schema.org structured data on recall detail + check tool pages
- Auto-generated sitemap with all URLs
- All pages have unique meta descriptions and canonical URLs
