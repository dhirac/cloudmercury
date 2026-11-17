"""Which fields and lists appear on each page of the management dashboard."""
from .models import FAQ, ProcessStep, Service, Stat, Value, WhyCard

# slug: (menu label, icon, description, [(group title, [fields])], [list slugs])
SECTIONS = {
    "hero": ("Header & hero", "home", "The first thing visitors see: headline, intro, buttons and the website picture.", [
        ("Header", ["nav_cta"]),
        ("Headline and intro", ["hero_title", "hero_highlight", "hero_lead", "hero_cta_primary", "hero_cta_secondary"]),
        ("Website picture", ["show_hero_visual", "hero_card_title",
                             "hero_stat1_label", "hero_stat1_value", "hero_stat2_label", "hero_stat2_value",
                             "hero_stat3_label", "hero_stat3_value",
                             "hero_float1_title", "hero_float1_text", "hero_float2_title", "hero_float2_text",
                             "hero_float3_title", "hero_float3_text"]),
        ("Technology strip", ["tech_title", "tech_list"]),
    ], []),
    "about": ("About & numbers", "users", "Who you are, the short points beside it and the numbers box.", [
        ("About", ["show_about", "about_kicker", "about_title", "about_intro", "about_body"]),
        ("Numbers box", ["trust_title", "trust_text"]),
    ], ["stats", "values"]),
    "services": ("Services", "box", "Your service cards. Large cards also appear in the contact form's list.", [
        ("Section heading", ["services_kicker", "services_title", "services_lead"]),
    ], ["services"]),
    "process": ("How we work", "sparkle", "The numbered steps of your process.", [
        ("Section heading", ["show_process", "process_kicker", "process_title", "process_lead"]),
    ], ["steps"]),
    "why": ("Why choose us", "shield", "Reasons to choose you and the industries you serve.", [
        ("Section heading", ["show_why", "why_kicker", "why_title", "why_lead"]),
        ("Industries", ["industries"]),
    ], ["why"]),
    "faq": ("FAQ", "help", "Questions and answers.", [
        ("Section heading", ["show_faq", "faq_kicker", "faq_title"]),
    ], ["faqs"]),
    "contact": ("Contact & banner", "phone", "Contact details, form texts and the call-to-action banner.", [
        ("Call-to-action banner", ["show_cta", "cta_title", "cta_text", "cta_button"]),
        ("Contact section", ["contact_kicker", "contact_title", "contact_lead"]),
        ("Contact details", ["email", "phone", "address1_title", "address1", "address2_title", "address2"]),
        ("Contact form", ["form_note", "form_success", "notify_email"]),
    ], []),
    "footer": ("Footer & social", "globe", "Footer text and links to your social media.", [
        ("Footer", ["footer_text", "footer_note"]),
        ("Social media", ["linkedin", "facebook", "instagram", "x_twitter"]),
    ], []),
    "branding": ("Logo & colours", "sparkle", "Company name, logos, tab icon and main colours.", [
        ("Name", ["site_name"]),
        ("Logos", ["logo", "logo_light", "favicon"]),
        ("Colours", ["primary_color", "accent_color", "dark_color"]),
    ], []),
    "seo": ("Google & SEO", "chart", "How your site appears in Google, and your tracking code.", [
        ("Search results", ["seo_title", "seo_description"]),
        ("Tracking", ["gtm_id"]),
    ], []),
}

# slug: (Model, singular label, plural label, fields, title attribute, extra column)
LISTS = {
    "services": (Service, "service", "Service cards", ["title", "kind", "text", "bullets", "icon", "color", "badge",
                                                      "link_text", "is_active"], "title", "kind"),
    "stats": (Stat, "number", "Numbers", ["value", "label", "is_active"], "value", "label"),
    "values": (Value, "point", "About points", ["title", "text", "icon", "color", "is_active"], "title", None),
    "steps": (ProcessStep, "step", "Steps", ["title", "text", "is_active"], "title", None),
    "why": (WhyCard, "reason", "Reasons", ["title", "text", "icon", "color", "is_active"], "title", None),
    "faqs": (FAQ, "question", "Questions", ["question", "answer", "is_active"], "question", None),
}

LIST_SECTION = {slug: sec for sec, data in SECTIONS.items() for slug in data[4]}
