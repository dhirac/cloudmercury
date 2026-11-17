"""Single source of truth for the plans shown on the home page and in the
"Order a service" form. Edit prices and features here – PLACEHOLDER prices,
set your real ones before going live.
"""

CATEGORIES = [
    ("web_hosting", "Web hosting"),
    ("email_hosting", "Email hosting"),
    ("saas", "Software & SaaS development"),
    ("marketing", "Digital marketing"),
    ("domain", "Domain"),
]

HOSTING_PLANS = [
    {
        "slug": "starter", "name": "Starter", "price": "4", "period": "/month",
        "for": "A single site or portfolio",
        "features": ["1 website", "20 GB NVMe storage", "Free SSL certificate", "Daily backups, kept 14 days",
                     "2 email accounts"],
    },
    {
        "slug": "business", "name": "Business", "price": "12", "period": "/month", "featured": True,
        "for": "Growing businesses and shops",
        "features": ["10 websites", "100 GB NVMe storage", "Global CDN and staging sites", "Daily backups, kept 30 days",
                     "10 email accounts", "Malware scanning"],
    },
    {
        "slug": "scale", "name": "Scale", "price": "29", "period": "/month",
        "for": "High-traffic sites and web apps",
        "features": ["Unlimited websites", "250 GB NVMe storage", "Dedicated CPU and RAM", "Hourly backups",
                     "25 email accounts", "Priority support in 1 hour"],
    },
]

EMAIL_PLANS = [
    {"slug": "mail-basic", "name": "Mail Basic", "price": "1.50", "period": "/mailbox a month",
     "features": ["10 GB per mailbox", "Your own domain", "Spam and virus filtering", "Webmail, IMAP and phone apps"]},
    {"slug": "mail-pro", "name": "Mail Pro", "price": "3.50", "period": "/mailbox a month",
     "features": ["50 GB per mailbox", "Shared calendars and contacts", "Email archiving for 7 years",
                  "DKIM, SPF and DMARC set up for you"]},
]

ORDER_PLANS = {
    "web_hosting": [(p["slug"], f'{p["name"]} – €{p["price"]}{p["period"]}') for p in HOSTING_PLANS],
    "email_hosting": [(p["slug"], f'{p["name"]} – €{p["price"]}{p["period"]}') for p in EMAIL_PLANS],
    "saas": [("discovery", "Discovery workshop"), ("mvp", "MVP build"), ("product", "Full product build"),
             ("retainer", "Ongoing development retainer")],
    "marketing": [("seo", "SEO"), ("ppc", "Paid ads (Google, Meta, LinkedIn)"), ("social", "Social media"),
                  ("content", "Content marketing"), ("growth", "Full growth package")],
    "domain": [("register", "Register a new domain"), ("transfer", "Transfer a domain to us")],
}

ALL_PLAN_CHOICES = [c for plans in ORDER_PLANS.values() for c in plans]
