#!/usr/bin/env python3
"""
Static Site Generator for CPSC Recall Tracker (v2 - Monetization Edition)
Reads recall data from /data/recalls.json and generates:
- index.html (homepage with latest recalls + category grid)
- /recall/{slug}.html (detail page per recall WITH affiliate recommendations)
- /categories/{slug}.html (category listing pages)
- /brands/{slug}.html (brand index pages)
- /check/ (Is My Product Recalled? lookup tool)
- sitemap.xml & robots.txt

Monetization: Amazon affiliate links, Beehiiv email capture, cross-links to newparentreviews.net
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from html import escape

# --- Config ---
PROJECT_DIR = Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR
SITE_URL = "https://newparentreviews.net/recalls"
MAIN_SITE_URL = "https://newparentreviews.net"
SITE_NAME = "Parent Recall Watch"

# ========================================================
# AMAZON AFFILIATE TAG - Replace with your actual tag!
# ========================================================
AMAZON_TAG = "newparentrevi-20"

# ========================================================
# BEEHIIV - Replace with your actual publication ID
# ========================================================
BEEHIIV_PUBLICATION_ID = "pub_4134289b-7960-4896-a605-f43c1876d35b"

RECALLS_PER_PAGE = 20

# --- Category Config ---
CATEGORY_CONFIG = {
    "cribs-cradles": {"name": "Cribs & Cradles", "icon": "&#128716;", "description": "Crib, cradle, and bassinet recalls that every parent should know about."},
    "strollers": {"name": "Strollers", "icon": "&#128694;", "description": "Stroller and carriage safety recalls."},
    "car-seats": {"name": "Car Seats", "icon": "&#128663;", "description": "Car seat, booster seat, and infant carrier recalls."},
    "toys": {"name": "Toys", "icon": "&#129528;", "description": "Toy recalls including choking hazards, lead paint, and more."},
    "clothing": {"name": "Children's Clothing", "icon": "&#128085;", "description": "Children's clothing recalls for flammability, choking hazards, and more."},
    "high-chairs": {"name": "High Chairs", "icon": "&#129473;", "description": "High chair and feeding seat recalls."},
    "play-yards": {"name": "Play Yards & Playpens", "icon": "&#127968;", "description": "Play yard, playpen, and pack-n-play recalls."},
    "baby-carriers": {"name": "Baby Carriers", "icon": "&#128118;", "description": "Baby carrier, sling, and wrap recalls."},
    "swings-bouncers": {"name": "Swings & Bouncers", "icon": "&#127904;", "description": "Baby swing, bouncer, and rocker recalls."},
    "baby-gates": {"name": "Baby Gates", "icon": "&#128682;", "description": "Safety gate and baby gate recalls."},
    "furniture": {"name": "Children's Furniture", "icon": "&#128221;", "description": "Children's furniture recalls including tip-over hazards."},
    "monitors": {"name": "Baby Monitors", "icon": "&#128247;", "description": "Baby monitor and nursery camera recalls."},
    "feeding": {"name": "Feeding & Nursing", "icon": "&#127868;", "description": "Bottle, pacifier, breast pump, and feeding product recalls."},
    "bath": {"name": "Bath Products", "icon": "&#128704;", "description": "Baby bath tub, bath seat, and bath toy recalls."},
    "other": {"name": "Other Products", "icon": "&#128221;", "description": "Other parent and child product recalls."},
}

# --- Affiliate Replacement Product Suggestions by Category ---
# Amazon search URLs with affiliate tag — high-intent clicks
AFFILIATE_RECOMMENDATIONS = {
    "cribs-cradles": [
        {"title": "Top-Rated Cribs", "search": "best+rated+baby+crib", "text": "See highest-rated cribs on Amazon"},
        {"title": "Bassinets", "search": "best+bassinet+baby", "text": "Top bassinets for newborns"},
    ],
    "strollers": [
        {"title": "Best Strollers", "search": "best+rated+stroller+baby", "text": "Top-rated strollers on Amazon"},
        {"title": "Lightweight Strollers", "search": "lightweight+umbrella+stroller", "text": "Lightweight travel strollers"},
    ],
    "car-seats": [
        {"title": "Safest Car Seats", "search": "safest+convertible+car+seat+baby", "text": "Highest-rated car seats"},
        {"title": "Infant Car Seats", "search": "infant+car+seat+base", "text": "Best infant car seats"},
        {"title": "Booster Seats", "search": "booster+seat+kids", "text": "Top booster seats for older kids"},
    ],
    "toys": [
        {"title": "Safe Baby Toys", "search": "safe+baby+toys+bpa+free", "text": "BPA-free safe baby toys"},
        {"title": "Toddler Toys", "search": "best+toddler+toys+educational", "text": "Top educational toddler toys"},
    ],
    "clothing": [
        {"title": "Organic Kids Pajamas", "search": "organic+cotton+kids+pajamas", "text": "Organic cotton kids' pajamas"},
        {"title": "Safe Sleepwear", "search": "flame+resistant+children+sleepwear", "text": "Flame-resistant children's sleepwear"},
    ],
    "high-chairs": [
        {"title": "Best High Chairs", "search": "best+rated+high+chair+baby", "text": "Top-rated high chairs"},
        {"title": "Portable High Chairs", "search": "portable+travel+high+chair", "text": "Portable high chairs for travel"},
    ],
    "play-yards": [
        {"title": "Best Play Yards", "search": "best+pack+n+play+playard", "text": "Top pack-n-plays and play yards"},
    ],
    "baby-carriers": [
        {"title": "Best Baby Carriers", "search": "best+rated+baby+carrier+ergonomic", "text": "Ergonomic baby carriers"},
        {"title": "Baby Wraps", "search": "baby+wrap+carrier+newborn", "text": "Baby wraps for newborns"},
    ],
    "swings-bouncers": [
        {"title": "Baby Swings", "search": "best+baby+swing+portable", "text": "Top-rated baby swings"},
        {"title": "Baby Bouncers", "search": "best+baby+bouncer+seat", "text": "Best baby bouncer seats"},
    ],
    "baby-gates": [
        {"title": "Best Baby Gates", "search": "best+baby+gate+stairs+hardware+mount", "text": "Hardware-mounted stair gates (safest)"},
        {"title": "Wide Baby Gates", "search": "extra+wide+baby+gate", "text": "Extra-wide baby gates"},
    ],
    "furniture": [
        {"title": "Anti-Tip Furniture Straps", "search": "furniture+anti+tip+straps+anchors", "text": "Furniture anti-tip anchor kits"},
        {"title": "Safe Kids Dressers", "search": "kids+dresser+tip+resistant", "text": "Tip-resistant children's dressers"},
    ],
    "monitors": [
        {"title": "Best Baby Monitors", "search": "best+baby+monitor+camera+wifi", "text": "Top-rated baby monitors"},
    ],
    "feeding": [
        {"title": "Best Baby Bottles", "search": "best+baby+bottles+anti+colic", "text": "Anti-colic baby bottles"},
        {"title": "Pacifiers", "search": "best+pacifiers+newborn+orthodontic", "text": "Orthodontic pacifiers"},
    ],
    "bath": [
        {"title": "Baby Bath Tubs", "search": "best+baby+bath+tub+newborn", "text": "Best baby bath tubs"},
        {"title": "Bath Toys", "search": "mold+free+bath+toys+baby", "text": "Mold-free bath toys"},
    ],
    "other": [
        {"title": "Baby Safety Products", "search": "baby+proofing+safety+kit", "text": "Baby proofing safety kits"},
    ],
}

# Cross-link map: category -> relevant newparentreviews.net page path
# Update these when you have actual review pages
CROSS_LINKS = {
    "cribs-cradles": "/best-cribs",
    "strollers": "/best-strollers",
    "car-seats": "/best-car-seats",
    "toys": "/best-baby-toys",
    "high-chairs": "/best-high-chairs",
    "baby-carriers": "/best-baby-carriers",
    "monitors": "/best-baby-monitors",
    "feeding": "/best-baby-bottles",
}


# === Utility Functions ===

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text[:80]

def format_date(date_str: str) -> str:
    if not date_str:
        return "Unknown"
    try:
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return dt.strftime("%B %d, %Y")
    except (ValueError, TypeError):
        return date_str[:10] if date_str else "Unknown"

def get_recall_slug(recall: dict) -> str:
    num = recall.get("RecallNumber", "unknown")
    title = recall.get("Title", "")
    if title:
        return f"{num}-{slugify(title)}"
    return num

def truncate(text: str, length: int = 200) -> str:
    if not text:
        return ""
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + "..."

def get_brand_slug(name: str) -> str:
    return slugify(name.split("(")[0].strip())

def amazon_affiliate_url(search_term: str) -> str:
    return f"https://www.amazon.com/s?k={search_term}&tag={AMAZON_TAG}"


# === HTML Templates ===

def base_template(title: str, content: str, canonical: str = "", meta_desc: str = "", schema_json: str = "") -> str:
    schema_tag = ""
    if schema_json:
        schema_tag = f'<script type="application/ld+json">{schema_json}</script>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(title)} | {SITE_NAME}</title>
    <meta name="description" content="{escape(meta_desc or title)}">
    {f'<link rel="canonical" href="{canonical}">' if canonical else ''}
    <link rel="stylesheet" href="/assets/css/style.css">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>&#9888;</text></svg>">
    {schema_tag}
</head>
<body>
    <header class="site-header">
        <div class="container">
            <a href="/" class="site-logo"><span>&#9888;</span> {SITE_NAME}</a>
            <nav class="site-nav">
                <a href="/">Latest</a>
                <a href="/categories/">Categories</a>
                <a href="/brands/">Brands</a>
                <a href="/check/">Check Product</a>
                <a href="https://newparentreviews.com">Reviews</a>
            </nav>
        </div>
    </header>

    {content}

    <section class="email-signup" id="subscribe">
        <div class="container">
            <h2>Get Recall Alerts in Your Inbox</h2>
            <p>Join {SITE_NAME} — we email you the moment a new child product recall drops. Free, no spam, unsubscribe anytime.</p>
            <form class="email-form" action="https://app.beehiiv.com/subscribe/{BEEHIIV_PUBLICATION_ID}" method="POST" target="_blank">
                <input type="email" name="email" placeholder="your@email.com" aria-label="Email address" required>
                <button type="submit">Get Alerts</button>
            </form>
            <p style="font-size:0.75rem;color:#9ca3af;margin-top:8px;">Powered by Beehiiv. We never share your email.</p>
        </div>
    </section>

    <footer class="site-footer">
        <div class="container">
            <p>Data sourced from <a href="https://www.cpsc.gov" target="_blank" rel="noopener">CPSC.gov</a>.
            Not affiliated with the U.S. Consumer Product Safety Commission.</p>
            <p style="margin-top:6px">Some links on this site are affiliate links. We may earn a small commission if you purchase through them, at no extra cost to you.</p>
            <p style="margin-top:8px">&copy; {datetime.now().year} {SITE_NAME} &middot;
            A <a href="/">NewParentReviews.net</a> project &middot;
            <a href="/brands/">Brands</a> &middot;
            <a href="/check/">Product Lookup</a></p>
        </div>
    </footer>
</body>
</html>"""


def affiliate_box_html(category: str) -> str:
    """Generate the affiliate recommendation box for a recall detail page."""
    recs = AFFILIATE_RECOMMENDATIONS.get(category, AFFILIATE_RECOMMENDATIONS["other"])

    links_html = ""
    for rec in recs:
        url = amazon_affiliate_url(rec["search"])
        links_html += f"""
        <a href="{url}" target="_blank" rel="noopener nofollow sponsored" class="affiliate-link">
            <span class="affiliate-link-title">{escape(rec['title'])}</span>
            <span class="affiliate-link-text">{escape(rec['text'])} &rarr;</span>
        </a>"""

    # Cross-link to newparentreviews.net if available
    cross_link_html = ""
    if category in CROSS_LINKS:
        cat_name = CATEGORY_CONFIG.get(category, {}).get("name", category)
        cross_link_html = f"""
        <div style="margin-top:12px;padding-top:12px;border-top:1px solid #e5e7eb;">
            <a href="{MAIN_SITE_URL}{CROSS_LINKS[category]}" style="font-size:0.9rem;font-weight:600;">
                &#128218; Read our {cat_name} reviews on NewParentReviews &rarr;
            </a>
        </div>"""

    return f"""
    <div class="affiliate-box">
        <h3>&#128722; Need a Safe Replacement?</h3>
        <p>If your product was recalled, here are top-rated alternatives:</p>
        <div class="affiliate-links">
            {links_html}
        </div>
        {cross_link_html}
    </div>"""


def recall_card_html(recall: dict) -> str:
    slug = get_recall_slug(recall)
    date = format_date(recall.get("RecallDate", ""))
    title = recall.get("Title") or "Untitled Recall"
    cat = recall.get("_category", "other")
    cat_name = CATEGORY_CONFIG.get(cat, {}).get("name", cat.replace("-", " ").title())
    recall_num = recall.get("RecallNumber", "")

    desc = recall.get("Description", "")
    if not desc:
        for p in recall.get("Products", []):
            desc = p.get("Description", "")
            if desc:
                break

    hazard = ""
    for h in recall.get("Hazards", []):
        hazard = h.get("Name", "")
        if hazard:
            break

    remedy = ""
    for r in recall.get("Remedies", []):
        remedy = r.get("Name", "")
        if remedy:
            break

    # Product details
    product_details = ""
    for p in recall.get("Products", []):
        pname = p.get("Name", "")
        pdesc = p.get("Description", "")
        units = p.get("NumberOfUnits", "")
        parts = []
        if pname:
            parts.append(f"<strong>{escape(pname)}</strong>")
        if pdesc:
            parts.append(escape(pdesc))
        if units:
            parts.append(f"<em>Units: {escape(str(units))}</em>")
        if parts:
            product_details = "<p>" + "</p><p>".join(parts) + "</p>"
        break

    # Consumer contact
    contact_html = ""
    contacts = recall.get("Consumers", [])
    if contacts:
        c = contacts[0]
        phone = c.get("Phone", "")
        url = c.get("URL", "")
        name = c.get("Name", "")
        parts = []
        if name:
            parts.append(escape(name))
        if phone:
            parts.append(escape(phone))
        if url:
            parts.append(f'<a href="{escape(url)}" target="_blank" rel="noopener">{escape(url)}</a>')
        if parts:
            contact_html = f'<p class="recall-description"><strong>Contact:</strong> {" | ".join(parts)}</p>'

    # CPSC link
    cpsc_url = recall.get("URL", f"https://www.cpsc.gov/Recalls")
    cpsc_link = f'<a href="{escape(cpsc_url)}" target="_blank" rel="noopener" style="font-size:0.85rem;">View on CPSC.gov &rarr;</a>'

    img_html = ""
    images = recall.get("Images", [])
    if images:
        img_url = images[0].get("URL", "")
        if img_url:
            img_html = f'<img src="{escape(img_url)}" alt="{escape(title)}" class="recall-image" loading="lazy">'

    # Brand link
    brand = ""
    brand_slug_str = ""
    for m in recall.get("Manufacturers", []):
        brand = m.get("Name", "")
        if brand:
            brand_slug_str = get_brand_slug(brand)
            break

    brand_html = f'<span style="font-size:0.85rem;color:#6b7280;">By <a href="/brands/{escape(brand_slug_str)}.html">{escape(brand)}</a></span>' if brand else ""

    # Affiliate links for this category
    recs = AFFILIATE_RECOMMENDATIONS.get(cat, AFFILIATE_RECOMMENDATIONS.get("other", []))
    aff_links = ""
    for rec in recs[:2]:
        url = amazon_affiliate_url(rec["search"])
        aff_links += f'<a href="{url}" target="_blank" rel="noopener nofollow sponsored" class="affiliate-link"><span class="affiliate-link-title">{escape(rec["title"])}</span><span class="affiliate-link-text">{escape(rec["text"])} &rarr;</span></a>'
    aff_html = f'<div class="affiliate-box" style="margin-top:12px;"><h3>&#128722; Need a Safe Replacement?</h3><div class="affiliate-links">{aff_links}</div></div>' if aff_links else ""

    recall_num_html = f'<span style="font-size:0.8rem;color:#9ca3af;">Recall #{escape(str(recall_num))}</span>' if recall_num else ""

    return f"""
    <article class="recall-card" id="recall-{escape(slug)}">
        {img_html}
        <div class="recall-meta">
            <span class="recall-date">{date}</span>
            <span class="recall-badge">{escape(cat_name)}</span>
            {recall_num_html}
        </div>
        <h2 class="recall-title" style="font-size:1.1rem;"><a href="/recall/{escape(slug)}.html">{escape(title)}</a></h2>
        {brand_html}
        {f'<div style="margin-top:10px;"><p class="recall-description"><strong>&#9888;&#65039; Hazard:</strong> {escape(hazard)}</p></div>' if hazard else ''}
        {f'<p class="recall-description"><strong>&#128295; Remedy:</strong> {escape(remedy)}</p>' if remedy else ''}
        {f'<div style="margin-top:8px;font-size:0.9rem;color:#4b5563;">{product_details}</div>' if product_details else ''}
        {contact_html}
        <div style="margin-top:8px;">{cpsc_link}</div>
        {aff_html}
    </article>"""


# === Page Generators ===

def generate_index(recalls: list):
    print("Generating index.html...")
    total = len(recalls)
    this_year = [r for r in recalls if r.get("RecallDate", "").startswith(str(datetime.now().year))]
    categories_with_data = set(r.get("_category", "other") for r in recalls)

    cat_grid = ""
    cat_counts = {}
    for r in recalls:
        cat = r.get("_category", "other")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    for slug, config in CATEGORY_CONFIG.items():
        count = cat_counts.get(slug, 0)
        if count > 0:
            cat_grid += f"""
            <a href="/categories/{slug}.html" class="category-card">
                <div class="category-icon">{config['icon']}</div>
                <div class="category-name">{config['name']}</div>
                <div class="category-count">{count} recall{'s' if count != 1 else ''}</div>
            </a>"""

    latest = recalls[:10]
    recall_cards = "".join(recall_card_html(r) for r in latest)

    content = f"""
    <section class="alert-banner" id="latest-alert">
        &#9888; Latest: <a href="/recall/{get_recall_slug(recalls[0])}.html" style="color:inherit;text-decoration:underline;">{escape(truncate(recalls[0].get('Title', ''), 80))}</a> ({format_date(recalls[0].get('RecallDate', ''))})
    </section>

    <section class="hero">
        <div class="container">
            <h1>Child Product Recalls You Need to Know</h1>
            <p>We monitor CPSC recalls daily so you don't have to. Check if your baby gear is safe.</p>
            <div style="margin-top:20px;">
                <a href="/check/" class="cta-button" style="background:#2563eb;font-size:1rem;padding:14px 28px;">&#128269; Is My Product Recalled?</a>
            </div>
            <div class="stat-bar">
                <div class="stat-item">
                    <div class="stat-number">{total}</div>
                    <div class="stat-label">Recalls Tracked</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{len(this_year)}</div>
                    <div class="stat-label">This Year</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{len(categories_with_data)}</div>
                    <div class="stat-label">Categories</div>
                </div>
            </div>
        </div>
    </section>

    <section class="categories-section">
        <div class="container">
            <h2 class="section-title">Browse by Category</h2>
            <div class="categories-grid">{cat_grid}</div>
        </div>
    </section>

    <section class="recalls-section">
        <div class="container">
            <h2 class="section-title">Latest Recalls</h2>
            <div id="recalls-list">{recall_cards}</div>
            <div class="pagination">
                <a href="/all-recalls.html">View All Recalls &rarr;</a>
            </div>
        </div>
    </section>"""

    meta = "Daily CPSC child product recall tracker. Check if your cribs, car seats, toys, strollers, and baby gear have been recalled."
    html = base_template("Child Product Recalls", content, f"{SITE_URL}/", meta)
    (OUTPUT_DIR / "index.html").write_text(html)


def generate_recall_detail(recall: dict):
    slug = get_recall_slug(recall)
    out_dir = OUTPUT_DIR / "recall"
    out_dir.mkdir(parents=True, exist_ok=True)

    title = recall.get("Title") or "Untitled Recall"
    date = format_date(recall.get("RecallDate", ""))
    num = recall.get("RecallNumber", "")
    cat = recall.get("_category", "other")
    cat_name = CATEGORY_CONFIG.get(cat, {}).get("name", "Other")

    products_html = ""
    for p in recall.get("Products", []):
        name = p.get("Name", "Unknown")
        desc = p.get("Description", "")
        units = p.get("NumberOfUnits", "")
        products_html += f"<p><strong>{escape(name)}</strong></p>"
        if desc:
            products_html += f"<p>{escape(desc)}</p>"
        if units:
            products_html += f"<p><em>Units: {escape(str(units))}</em></p>"

    hazards_html = ""
    for h in recall.get("Hazards", []):
        hazards_html += f"<p>{escape(h.get('Name', ''))}</p>"

    remedies_html = ""
    for r in recall.get("Remedies", []):
        remedies_html += f"<p>{escape(r.get('Name', ''))}</p>"

    images_html = ""
    for img in recall.get("Images", []):
        url = img.get("URL", "")
        if url:
            images_html += f'<img src="{escape(url)}" alt="{escape(title)}" style="max-width:100%;border-radius:8px;margin-bottom:12px;" loading="lazy">'

    mfg_html = ""
    brand_name = ""
    for m in recall.get("Manufacturers", []):
        brand_name = m.get("Name", "Unknown")
        brand_sl = get_brand_slug(brand_name)
        mfg_html += f'<p><a href="/brands/{brand_sl}.html">{escape(brand_name)}</a></p>'
    for m in recall.get("ManufacturerCountries", []):
        mfg_html += f"<p><em>Country: {escape(m.get('Country', ''))}</em></p>"

    contact = escape(recall.get("ConsumerContact", ""))
    cpsc_url = recall.get("URL", "")

    # Affiliate recommendation box
    aff_box = affiliate_box_html(cat)

    # Schema.org structured data for SEO
    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "Product",
        "name": title,
        "description": recall.get("Description", ""),
        "review": {
            "@type": "Review",
            "reviewBody": f"This product has been recalled by the CPSC. {hazards_html[:200]}",
            "author": {"@type": "Organization", "name": "CPSC"}
        }
    })

    content = f"""
    <div class="container">
        <nav class="breadcrumb">
            <a href="/">Home</a> <span>&rsaquo;</span>
            <a href="/categories/{escape(cat)}.html">{escape(cat_name)}</a> <span>&rsaquo;</span>
            <span>{escape(truncate(title, 60))}</span>
        </nav>
    </div>

    <section class="recall-detail">
        <div class="container">
            <div class="recall-meta" style="margin-bottom:16px;">
                <span class="recall-badge">RECALLED</span>
                <span class="recall-date">{date}</span>
                <span class="recall-date">Recall #{escape(num)}</span>
            </div>
            <h1>{escape(title)}</h1>

            <div class="detail-grid">
                <div class="detail-main">
                    {f'<div class="detail-section">{images_html}</div>' if images_html else ''}

                    <div class="detail-section">
                        <h2>Product Details</h2>
                        {products_html or '<p>No product details available.</p>'}
                    </div>

                    {f'<div class="detail-section"><h2>Hazard</h2>{hazards_html}</div>' if hazards_html else ''}
                    {f'<div class="detail-section"><h2>Remedy</h2>{remedies_html}</div>' if remedies_html else ''}

                    {aff_box}

                    {f'<div class="detail-section"><h2>Consumer Contact</h2><p>{contact}</p></div>' if contact else ''}
                    {f'<p style="margin-top:20px;"><a href="{escape(cpsc_url)}" target="_blank" rel="noopener">View on CPSC.gov &rarr;</a></p>' if cpsc_url else ''}
                </div>

                <div class="detail-sidebar">
                    <div class="info-box">
                        <h3>Recall Date</h3>
                        <p>{date}</p>
                    </div>
                    <div class="info-box">
                        <h3>Category</h3>
                        <p><a href="/categories/{escape(cat)}.html">{escape(cat_name)}</a></p>
                    </div>
                    {f'<div class="info-box"><h3>Manufacturer</h3>{mfg_html}</div>' if mfg_html else ''}
                    <div class="info-box">
                        <h3>Recall Number</h3>
                        <p>{escape(num)}</p>
                    </div>

                    <div class="cta-box">
                        <h3>Have this product?</h3>
                        <p>Stop using it immediately and follow the remedy instructions above.</p>
                        {f'<a href="{escape(cpsc_url)}" target="_blank" rel="noopener" class="cta-button">Report on CPSC.gov</a>' if cpsc_url else ''}
                    </div>

                    <div class="info-box" style="margin-top:16px;background:#eff6ff;border-color:#bfdbfe;">
                        <h3>&#128276; Get Alerts</h3>
                        <p style="font-size:0.85rem;">Never miss a recall. <a href="#subscribe">Subscribe to free email alerts</a>.</p>
                    </div>
                </div>
            </div>
        </div>
    </section>"""

    meta = f"CPSC recall: {title}. Check if you own this product, what the hazard is, and find safe replacements."
    html = base_template(title, content, f"{SITE_URL}/recall/{slug}.html", meta, schema)
    (out_dir / f"{slug}.html").write_text(html)


def generate_category_pages(recalls: list):
    print("Generating category pages...")
    cat_dir = OUTPUT_DIR / "categories"
    cat_dir.mkdir(parents=True, exist_ok=True)

    by_cat = {}
    for r in recalls:
        cat = r.get("_category", "other")
        by_cat.setdefault(cat, []).append(r)

    for slug, cat_recalls in by_cat.items():
        config = CATEGORY_CONFIG.get(slug, {"name": slug.replace("-", " ").title(), "icon": "&#128221;", "description": ""})
        cards = "".join(recall_card_html(r) for r in cat_recalls)

        # Affiliate suggestions for category page too
        recs = AFFILIATE_RECOMMENDATIONS.get(slug, [])
        aff_html = ""
        if recs:
            links = ""
            for rec in recs[:2]:
                url = amazon_affiliate_url(rec["search"])
                links += f'<a href="{url}" target="_blank" rel="noopener nofollow sponsored" class="affiliate-link"><span class="affiliate-link-title">{escape(rec["title"])}</span><span class="affiliate-link-text">{escape(rec["text"])} &rarr;</span></a>'
            aff_html = f'<div class="affiliate-box" style="margin-bottom:24px;"><h3>&#128722; Looking for Safe {config["name"]}?</h3><div class="affiliate-links">{links}</div></div>'

        # Cross-link
        cross_html = ""
        if slug in CROSS_LINKS:
            cross_html = f'<p style="text-align:center;margin-bottom:24px;"><a href="{MAIN_SITE_URL}{CROSS_LINKS[slug]}" style="font-weight:600;">&#128218; Read our full {config["name"]} reviews on NewParentReviews.net &rarr;</a></p>'

        content = f"""
        <div class="container">
            <nav class="breadcrumb">
                <a href="/">Home</a> <span>&rsaquo;</span>
                <a href="/categories/">Categories</a> <span>&rsaquo;</span>
                <span>{config['name']}</span>
            </nav>
        </div>
        <section class="hero" style="padding:32px 0;">
            <div class="container">
                <div style="font-size:3rem;">{config['icon']}</div>
                <h1>{config['name']} Recalls</h1>
                <p>{config['description']}</p>
                <div class="stat-bar">
                    <div class="stat-item">
                        <div class="stat-number">{len(cat_recalls)}</div>
                        <div class="stat-label">Total Recalls</div>
                    </div>
                </div>
            </div>
        </section>
        <section class="recalls-section">
            <div class="container">
                {aff_html}
                {cross_html}
                {cards}
            </div>
        </section>"""

        meta = f"{config['name']} recalls for parents. {len(cat_recalls)} tracked. {config['description']}"
        html = base_template(f"{config['name']} Recalls", content, f"{SITE_URL}/categories/{slug}.html", meta)
        (cat_dir / f"{slug}.html").write_text(html)

    # Category index
    cat_grid = ""
    for slug, config in CATEGORY_CONFIG.items():
        count = len(by_cat.get(slug, []))
        if count > 0:
            cat_grid += f"""
            <a href="/categories/{slug}.html" class="category-card">
                <div class="category-icon">{config['icon']}</div>
                <div class="category-name">{config['name']}</div>
                <div class="category-count">{count} recall{'s' if count != 1 else ''}</div>
            </a>"""

    content = f"""
    <div class="container"><nav class="breadcrumb"><a href="/">Home</a> <span>&rsaquo;</span> <span>Categories</span></nav></div>
    <section class="hero" style="padding:32px 0;"><div class="container"><h1>Recall Categories</h1><p>Browse child product recalls by category</p></div></section>
    <section class="categories-section" style="padding-bottom:48px;"><div class="container"><div class="categories-grid">{cat_grid}</div></div></section>"""
    html = base_template("All Categories", content, f"{SITE_URL}/categories/", "Browse child product recalls by category.")
    (cat_dir / "index.html").write_text(html)


def generate_brand_pages(recalls: list):
    """Generate a page per manufacturer/brand showing all their recalls."""
    print("Generating brand pages...")
    brand_dir = OUTPUT_DIR / "brands"
    brand_dir.mkdir(parents=True, exist_ok=True)

    by_brand = {}
    for r in recalls:
        for m in r.get("Manufacturers", []):
            name = m.get("Name", "").strip()
            if name:
                by_brand.setdefault(name, []).append(r)

    for brand_name, brand_recalls in sorted(by_brand.items()):
        slug = get_brand_slug(brand_name)
        cards = "".join(recall_card_html(r) for r in brand_recalls)

        content = f"""
        <div class="container">
            <nav class="breadcrumb">
                <a href="/">Home</a> <span>&rsaquo;</span>
                <a href="/brands/">Brands</a> <span>&rsaquo;</span>
                <span>{escape(brand_name)}</span>
            </nav>
        </div>
        <section class="hero" style="padding:32px 0;">
            <div class="container">
                <h1>{escape(brand_name)} Recalls</h1>
                <p>All tracked CPSC recalls for products made by {escape(brand_name)}.</p>
                <div class="stat-bar">
                    <div class="stat-item">
                        <div class="stat-number">{len(brand_recalls)}</div>
                        <div class="stat-label">Total Recalls</div>
                    </div>
                </div>
            </div>
        </section>
        <section class="recalls-section">
            <div class="container">{cards}</div>
        </section>"""

        meta = f"{brand_name} product recalls. {len(brand_recalls)} tracked recalls. Check if your {brand_name} products have been recalled."
        html = base_template(f"{brand_name} Recalls", content, f"{SITE_URL}/brands/{slug}.html", meta)
        (brand_dir / f"{slug}.html").write_text(html)

    # Brand index page
    brand_grid = ""
    for name in sorted(by_brand.keys()):
        slug = get_brand_slug(name)
        count = len(by_brand[name])
        brand_grid += f"""
        <a href="/brands/{slug}.html" class="category-card">
            <div class="category-name">{escape(name)}</div>
            <div class="category-count">{count} recall{'s' if count != 1 else ''}</div>
        </a>"""

    content = f"""
    <div class="container"><nav class="breadcrumb"><a href="/">Home</a> <span>&rsaquo;</span> <span>Brands</span></nav></div>
    <section class="hero" style="padding:32px 0;">
        <div class="container">
            <h1>Recalls by Brand</h1>
            <p>Find all CPSC recalls for a specific manufacturer or brand.</p>
        </div>
    </section>
    <section class="categories-section" style="padding-bottom:48px;">
        <div class="container">
            <div class="categories-grid">{brand_grid}</div>
        </div>
    </section>"""

    html = base_template("Recalls by Brand", content, f"{SITE_URL}/brands/", "Browse child product recalls by brand and manufacturer.")
    (brand_dir / "index.html").write_text(html)

    return by_brand


def generate_check_page(recalls: list):
    """Generate the 'Is My Product Recalled?' interactive lookup tool."""
    print("Generating check/index.html (product lookup tool)...")
    check_dir = OUTPUT_DIR / "check"
    check_dir.mkdir(parents=True, exist_ok=True)

    # Build a lightweight JSON index for client-side search
    search_index = []
    for r in recalls:
        products = []
        for p in r.get("Products", []):
            products.append(p.get("Name", ""))
        brands = [m.get("Name", "") for m in r.get("Manufacturers", [])]
        hazard = ""
        for h in r.get("Hazards", []):
            hazard = h.get("Name", "")
            break

        search_index.append({
            "t": r.get("Title", ""),
            "d": r.get("RecallDate", "")[:10],
            "p": " | ".join(products),
            "b": " | ".join(brands),
            "h": truncate(hazard, 120),
            "u": f"/recall/{get_recall_slug(r)}.html",
            "c": r.get("_category", "other"),
        })

    search_json = json.dumps(search_index)

    content = f"""
    <section class="hero">
        <div class="container">
            <h1>&#128269; Is My Product Recalled?</h1>
            <p>Type a product name, brand, or model number below to instantly check if it's been recalled.</p>
        </div>
    </section>

    <section class="search-section" style="padding:32px 0;">
        <div class="container">
            <div class="search-box" style="max-width:600px;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
                </svg>
                <input type="text" id="check-input" placeholder="e.g., Graco stroller, Fisher-Price swing, Britax car seat..." autofocus style="font-size:1.1rem;padding:14px 16px 14px 44px;">
            </div>
            <p style="text-align:center;font-size:0.8rem;color:#9ca3af;margin-top:8px;">
                Search across {len(recalls)} tracked recalls. Updated daily from CPSC.gov.
            </p>
        </div>
    </section>

    <section class="recalls-section" style="padding-top:0;">
        <div class="container">
            <div id="check-results"></div>
            <div id="check-empty" style="display:none;text-align:center;padding:40px 0;">
                <p style="font-size:1.2rem;color:#16a34a;font-weight:700;">&#9989; No recalls found matching your search.</p>
                <p style="color:#6b7280;margin-top:8px;">Your product doesn't appear in our recall database. You can also check directly on <a href="https://www.cpsc.gov/Recalls" target="_blank" rel="noopener">CPSC.gov</a>.</p>
            </div>
            <div id="check-prompt" style="text-align:center;padding:40px 0;color:#6b7280;">
                <p>Start typing to search...</p>
            </div>
        </div>
    </section>

    <section style="padding:0 0 40px;">
        <div class="container">
            <div class="affiliate-box">
                <h3>&#128722; Shop Safe Baby Products</h3>
                <p>Looking for products with top safety ratings?</p>
                <div class="affiliate-links">
                    <a href="{amazon_affiliate_url('best+rated+baby+products+safety')}" target="_blank" rel="noopener nofollow sponsored" class="affiliate-link">
                        <span class="affiliate-link-title">Top-Rated Baby Products</span>
                        <span class="affiliate-link-text">See Amazon's highest-rated baby gear &rarr;</span>
                    </a>
                    <a href="{MAIN_SITE_URL}" class="affiliate-link">
                        <span class="affiliate-link-title">NewParentReviews.net</span>
                        <span class="affiliate-link-text">Our expert baby product reviews &rarr;</span>
                    </a>
                </div>
            </div>
        </div>
    </section>

    <script>
    const recalls = {search_json};

    const input = document.getElementById('check-input');
    const results = document.getElementById('check-results');
    const empty = document.getElementById('check-empty');
    const prompt = document.getElementById('check-prompt');

    let debounceTimer;
    input.addEventListener('input', function() {{
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(doSearch, 200);
    }});

    function doSearch() {{
        const q = input.value.toLowerCase().trim();
        if (q.length < 2) {{
            results.innerHTML = '';
            empty.style.display = 'none';
            prompt.style.display = '';
            return;
        }}
        prompt.style.display = 'none';

        const words = q.split(/\\s+/);
        const matches = recalls.filter(r => {{
            const text = (r.t + ' ' + r.p + ' ' + r.b + ' ' + r.h).toLowerCase();
            return words.every(w => text.includes(w));
        }});

        if (matches.length === 0) {{
            results.innerHTML = '';
            empty.style.display = '';
            return;
        }}

        empty.style.display = 'none';
        results.innerHTML = matches.slice(0, 20).map(r => `
            <article class="recall-card">
                <div class="recall-meta">
                    <span class="recall-date">${{r.d}}</span>
                    <span class="recall-badge">RECALLED</span>
                </div>
                <h3 class="recall-title"><a href="${{r.u}}">${{r.t}}</a></h3>
                ${{r.b ? '<p class="recall-description"><strong>Brand:</strong> ' + r.b + '</p>' : ''}}
                ${{r.p ? '<p class="recall-description"><strong>Products:</strong> ' + r.p + '</p>' : ''}}
                ${{r.h ? '<p class="recall-description"><strong>Hazard:</strong> ' + r.h + '</p>' : ''}}
                <div class="recall-actions">
                    <a href="${{r.u}}">Full Details & Safe Alternatives</a>
                </div>
            </article>
        `).join('');
    }}
    </script>"""

    meta = "Check if your baby product has been recalled. Search by brand, product name, or model number. Free, instant CPSC recall lookup."
    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "WebApplication",
        "name": "Is My Product Recalled? - CPSC Recall Checker",
        "description": meta,
        "url": f"{SITE_URL}/check/",
        "applicationCategory": "UtilityApplication",
        "operatingSystem": "Web Browser"
    })
    html = base_template("Is My Product Recalled?", content, f"{SITE_URL}/check/", meta, schema)
    (check_dir / "index.html").write_text(html)


def generate_all_recalls_page(recalls: list):
    print("Generating all-recalls.html...")
    cards = "".join(recall_card_html(r) for r in recalls)

    content = f"""
    <div class="container"><nav class="breadcrumb"><a href="/">Home</a> <span>&rsaquo;</span> <span>All Recalls</span></nav></div>
    <section class="hero" style="padding:24px 0;"><div class="container"><h1>All Tracked Recalls ({len(recalls)})</h1></div></section>
    <section class="search-section"><div class="container"><div class="search-box">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
        <input type="text" id="search-input" placeholder="Search all recalls..." onkeyup="filterRecalls()">
    </div></div></section>
    <section class="recalls-section"><div class="container"><div id="recalls-list">{cards}</div></div></section>
    <script>
    function filterRecalls() {{
        const query = document.getElementById('search-input').value.toLowerCase();
        const cards = document.querySelectorAll('#recalls-list .recall-card');
        cards.forEach(card => {{
            const text = card.textContent.toLowerCase();
            card.style.display = text.includes(query) ? '' : 'none';
        }});
    }}
    </script>"""

    html = base_template("All Recalls", content, f"{SITE_URL}/all-recalls.html", "Complete list of tracked child product recalls.")
    (OUTPUT_DIR / "all-recalls.html").write_text(html)


def generate_sitemap(recalls: list, brands: dict):
    print("Generating sitemap.xml...")
    now = datetime.now().strftime("%Y-%m-%d")

    urls = [
        f'  <url><loc>{SITE_URL}/</loc><lastmod>{now}</lastmod><changefreq>daily</changefreq><priority>1.0</priority></url>',
        f'  <url><loc>{SITE_URL}/check/</loc><lastmod>{now}</lastmod><changefreq>daily</changefreq><priority>0.9</priority></url>',
        f'  <url><loc>{SITE_URL}/categories/</loc><lastmod>{now}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>',
        f'  <url><loc>{SITE_URL}/brands/</loc><lastmod>{now}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>',
        f'  <url><loc>{SITE_URL}/all-recalls.html</loc><lastmod>{now}</lastmod><changefreq>daily</changefreq><priority>0.7</priority></url>',
    ]

    categories_seen = set()
    for r in recalls:
        cat = r.get("_category", "other")
        if cat not in categories_seen:
            categories_seen.add(cat)
            urls.append(f'  <url><loc>{SITE_URL}/categories/{cat}.html</loc><lastmod>{now}</lastmod><changefreq>weekly</changefreq><priority>0.7</priority></url>')

    for brand_name in brands:
        slug = get_brand_slug(brand_name)
        urls.append(f'  <url><loc>{SITE_URL}/brands/{slug}.html</loc><lastmod>{now}</lastmod><changefreq>weekly</changefreq><priority>0.6</priority></url>')

    for r in recalls:
        slug = get_recall_slug(r)
        date = r.get("RecallDate", now)[:10]
        urls.append(f'  <url><loc>{SITE_URL}/recall/{slug}.html</loc><lastmod>{date}</lastmod><changefreq>monthly</changefreq><priority>0.6</priority></url>')

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""
    (OUTPUT_DIR / "sitemap.xml").write_text(sitemap)


def generate_robots_txt():
    robots = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""
    (OUTPUT_DIR / "robots.txt").write_text(robots)


def main():
    print(f"=== {SITE_NAME} - Static Site Generator v2 ===\n")

    data_file = DATA_DIR / "recalls.json"
    if not data_file.exists():
        print(f"ERROR: No data file at {data_file}. Run fetch_recalls.py first!")
        return

    with open(data_file) as f:
        recalls = json.load(f)

    print(f"Loaded {len(recalls)} recalls\n")

    generate_index(recalls)

    print(f"Generating {len(recalls)} recall detail pages (with affiliate links)...")
    for recall in recalls:
        generate_recall_detail(recall)

    generate_category_pages(recalls)
    brands = generate_brand_pages(recalls)
    generate_check_page(recalls)
    generate_all_recalls_page(recalls)
    generate_sitemap(recalls, brands)
    generate_robots_txt()

    print(f"\nDone! Site generated in {OUTPUT_DIR}")
    print(f"Total HTML files: {sum(1 for _ in OUTPUT_DIR.rglob('*.html'))}")
    print(f"Brand pages: {len(brands)}")
    print(f"Sitemap URLs: {sum(1 for line in (OUTPUT_DIR / 'sitemap.xml').read_text().split(chr(10)) if '<loc>' in line)}")


if __name__ == "__main__":
    main()
