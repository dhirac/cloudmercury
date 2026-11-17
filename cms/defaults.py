"""Starting content: the text the site had before the dashboard existed."""

SETTINGS = dict(
    site_name="CloudMercury",
    seo_title="CloudMercury – Digital marketing, software & SaaS development, web and email hosting",
    seo_description="CloudMercury helps businesses grow online with digital marketing, custom software and SaaS "
                    "development, web hosting and professional business email.",
    gtm_id="GTM-57G52HK",
    nav_cta="Get a free quote",
    hero_title="We build, host and grow your",
    hero_highlight="digital business",
    hero_lead="Marketing that brings in customers, software built around how you work, and hosting that keeps your "
              "website and email fast and secure. Everything your business needs to grow online, from one team.",
    hero_cta_primary="Get a free quote",
    hero_cta_secondary="Explore our services",
    hero_card_title="Website visitors",
    hero_stat1_label="Visitors", hero_stat1_value="24.8k",
    hero_stat2_label="New leads", hero_stat2_value="312",
    hero_stat3_label="Page speed", hero_stat3_value="98/100",
    hero_float1_title="Google ranking", hero_float1_text="Page 1 for 14 keywords",
    hero_float2_title="hello@yourbusiness.com", hero_float2_text="Delivered to inbox",
    hero_float3_title="SSL secured", hero_float3_text="Daily backups on",
    tech_title="Technologies we work with",
    tech_list="Google Cloud\nAWS\nPython & Django\nReact\nNode.js\nWordPress\nStripe\nGoogle Ads\nMeta Ads",
    about_kicker="About us",
    about_title="Your partner for everything digital",
    about_intro="Most businesses work with a separate agency, developer, hosting company and email provider. "
                "With CloudMercury you get one team that understands how all of it fits together.",
    about_body="CloudMercury is a cloud, software and digital marketing company. We help startups, local shops and "
               "growing companies build their online presence, launch software products and reach new customers."
               "\n\nIntegrity, transparency and a collaborative approach are at the core of everything we do. "
               "You always know what we're working on, what it costs and what results it brings.",
    trust_title="Trusted by businesses across Europe",
    trust_text="We work with companies in Portugal, the United Kingdom and beyond, from first website to full "
               "software platforms.",
    services_kicker="What we do",
    services_title="Services that help your business grow",
    services_lead="Pick one service or combine them. Everything is planned around your goals and your budget.",
    process_kicker="How we work",
    process_title="A simple process from first call to results",
    process_lead="We use agile methods with short cycles, so you see progress every week and can change direction "
                 "when you need to.",
    why_kicker="Why choose us",
    why_title="One goal: your success",
    why_lead="When you work with us, we focus on delivering quality work that makes a real difference to your "
             "business.",
    industries="Retail & e-commerce\nTourism & hospitality\nProfessional services\nHealth & wellness\nReal estate\n"
               "Education\nStartups",
    faq_kicker="FAQ",
    faq_title="Questions we often hear",
    cta_title="Ready to grow your business online?",
    cta_text="Tell us what you need and get a free, no-obligation quote within one business day.",
    cta_button="Get a free quote",
    contact_kicker="Contact us",
    contact_title="Let's talk about your project",
    contact_lead="Send us a message and we'll get back to you within one business day. No sign-up needed.",
    email="cloudinovater@gmail.com",
    phone="+351 969 952 428",
    address1_title="Headquarters, Portugal",
    address1="Rua João da Silva Marques, 2825-122 Caparica",
    address2_title="Office, United Kingdom",
    address2="Boston Parade, London W7 2DG",
    form_note="We only use your details to reply to your message.",
    form_success="Thank you! Your message has been sent. We'll reply within one business day.",
    footer_text="Quality digital services at fair prices. We value your time and work hard to meet every deadline.",
    footer_note="Made in Lisbon",
)

STATS = [("150+", "Happy clients"), ("210+", "Projects delivered"), ("600+", "Hours of support"),
         ("2", "Offices, Lisbon and London")]

VALUES = [
    ("sparkle", "violet", "Idea to execution",
     "From the first conversation to launch and beyond, we handle strategy, design, development and support."),
    ("chart", "pink", "Data-driven decisions",
     "We measure what matters, like leads, sales and speed, and use the numbers to improve every month."),
    ("users", "teal", "A team you can talk to",
     "You work directly with the people building your project, in English or Portuguese."),
]

SERVICES = [
    dict(kind="main", icon="chart", color="pink", title="Digital marketing",
         text="Get found by the right people and turn visitors into customers. We create data-driven campaigns and "
              "report on the results that matter: leads, sales and return on your budget.",
         bullets="Search engine optimisation (SEO)\nGoogle and Meta ads (PPC)\nSocial media marketing\n"
                 "Content and email marketing\nAnalytics and reporting\nMarketing strategy",
         link_text="Ask for a free marketing audit"),
    dict(kind="main", icon="code", color="amber", title="Software & SaaS development",
         text="From an idea on paper to a product your customers pay for. We design and build web apps, SaaS "
              "platforms and internal tools that are secure, fast and ready to scale.",
         bullets="Custom web applications\nSaaS products and MVPs\nWebsites and online shops\nAPIs and integrations\n"
                 "Payments and subscriptions\nMaintenance and support",
         link_text="Tell us about your idea"),
    dict(kind="main", icon="server", color="blue", title="Web hosting", badge="Launching soon",
         text="Fast and reliable hosting for websites, online shops and web apps. We take care of servers, security "
              "and backups, so your site stays online and loads quickly.",
         bullets="Managed WordPress hosting\nCloud hosting for web apps\nFree SSL certificates\nDaily backups\n"
                 "Domain registration\nFree website migration",
         link_text="Join the waiting list"),
    dict(kind="main", icon="mail", color="teal", title="Email hosting", badge="Launching soon",
         text="Professional email on your own domain, like you@yourbusiness.com. Secure, spam-filtered and set up "
              "correctly so your messages reach the inbox.",
         bullets="Email on your own domain\nSpam and virus protection\nWorks on phone and laptop\n"
                 "Shared calendars and contacts\nSPF, DKIM and DMARC setup\nMove from your old provider",
         link_text="Join the waiting list"),
    dict(kind="extra", icon="cloud", color="violet", title="Cloud & AI solutions",
         text="Move to the cloud, automate repetitive work and add AI features like chatbots and smart search to "
              "your products."),
    dict(kind="extra", icon="folder", color="violet", title="Data & analytics",
         text="Bring your data together in clear dashboards so you can see what's working and make better "
              "decisions."),
]

STEPS = [
    ("Discover", "A free call to understand your business, your customers and what you want to achieve."),
    ("Plan", "A clear proposal with scope, timeline and a fixed price, so there are no surprises."),
    ("Build & launch", "We design, develop and test, showing you progress along the way, then launch together."),
    ("Grow", "We support, measure and improve, helping you get more customers month after month."),
]

WHY = [
    ("users", "violet", "Highly qualified team",
     "Our team has over a decade of experience in software, cloud and marketing, working with businesses of every "
     "size."),
    ("wallet", "amber", "Fits your budget",
     "We find the right solution for your needs and keep costs fair, with clear prices agreed before we start."),
    ("clock", "teal", "Delivered on time",
     "Agile planning with Scrum helps us deliver every project on schedule, with regular updates along the way."),
]

FAQS = [
    ("How much does a project cost?",
     "It depends on what you need. After a free call we send a clear proposal with a fixed price, so you know the "
     "full cost before we start. We work with small businesses and larger companies alike."),
    ("How long does it take to build a website or app?",
     "A business website usually takes 2 to 4 weeks. A custom web app or SaaS product typically takes 2 to 4 months "
     "for the first version, depending on features."),
    ("When will web and email hosting be available?",
     "Our hosting and email services are launching soon. Send us a message and we'll let you know as soon as "
     "they're ready, and help you move over at no cost."),
    ("Can you improve my existing website or marketing?",
     "Yes. We can review your current site, search rankings and ads, then suggest improvements. Many clients start "
     "with a free audit."),
    ("Do you work with clients outside Portugal?",
     "Yes. We have offices in Lisbon and London and work with clients across Europe and beyond, in English and "
     "Portuguese."),
]


def seed(apps=None):
    """Fill empty tables with the starting content. Safe to run more than once."""
    if apps is None:
        from django.apps import apps as global_apps
        apps = global_apps
    get = lambda n: apps.get_model("cms", n)
    S = get("SiteSettings")
    if not S.objects.filter(pk=1).exists():
        S.objects.create(pk=1, **SETTINGS)
    if not get("Stat").objects.exists():
        for i, (v, l) in enumerate(STATS):
            get("Stat").objects.create(order=i, value=v, label=l)
    if not get("Value").objects.exists():
        for i, (ic, c, t, x) in enumerate(VALUES):
            get("Value").objects.create(order=i, icon=ic, color=c, title=t, text=x)
    if not get("Service").objects.exists():
        for i, d in enumerate(SERVICES):
            get("Service").objects.create(order=i, **d)
    if not get("ProcessStep").objects.exists():
        for i, (t, x) in enumerate(STEPS):
            get("ProcessStep").objects.create(order=i, title=t, text=x)
    if not get("WhyCard").objects.exists():
        for i, (ic, c, t, x) in enumerate(WHY):
            get("WhyCard").objects.create(order=i, icon=ic, color=c, title=t, text=x)
    if not get("FAQ").objects.exists():
        for i, (q, a) in enumerate(FAQS):
            get("FAQ").objects.create(order=i, question=q, answer=a)
