"""
Django settings for the CloudMercury project.

Secrets are read from environment variables. For local development you can
create a `.env` file next to manage.py (see .env.example) – it is loaded
automatically if present.
"""
import os
from importlib.util import find_spec
from pathlib import Path
from urllib.parse import parse_qsl, unquote, urlparse

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_dotenv(path):
    """Tiny .env loader so no extra dependency is needed."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in ("1", "true", "yes", "on")


def env_list(name, default=""):
    return [v.strip() for v in os.environ.get(name, default).split(",") if v.strip()]


# --- Core -------------------------------------------------------------------
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "dev-only-insecure-key-change-me",  # override in production!
)
DEBUG = env_bool("DJANGO_DEBUG", True)

ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS",
    "127.0.0.1,localhost,www.cloudinovater.com,cloudinovater.com",
)
CSRF_TRUSTED_ORIGINS = env_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "https://cloudinovater.com,https://www.cloudinovater.com",
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "landing",
    "accounts",
    "dashboard",
    "cms",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # WhiteNoise (added below when installed) serves static files in production.
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "accounts.context_processors.site",
                "cms.context_processors.nav",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# --- Database ----------------------------------------------------------------
# Production uses PostgreSQL, configured in .env in either of two ways:
#   DATABASE_URL=postgres://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require
# or separate variables:
#   POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT
# With neither set, the site falls back to the local SQLite file.

def _postgres_from_url(url):
    u = urlparse(url)
    if u.scheme not in ("postgres", "postgresql", "pgsql"):
        raise ValueError(f"DATABASE_URL must start with postgres:// (got {u.scheme}://)")
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": unquote(u.path.lstrip("/")),
        "USER": unquote(u.username or ""),
        "PASSWORD": unquote(u.password or ""),
        "HOST": u.hostname or "",
        "PORT": str(u.port or ""),
        "OPTIONS": dict(parse_qsl(u.query)),
    }


if os.environ.get("DATABASE_URL"):
    _db = _postgres_from_url(os.environ["DATABASE_URL"])
elif os.environ.get("POSTGRES_DB"):
    _db = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ.get("POSTGRES_USER", ""),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", ""),
        "HOST": os.environ.get("POSTGRES_HOST", "localhost"),
        "PORT": os.environ.get("POSTGRES_PORT", "5432"),
        "OPTIONS": {"sslmode": os.environ["POSTGRES_SSLMODE"]} if os.environ.get("POSTGRES_SSLMODE") else {},
    }
else:
    _db = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.environ.get("DJANGO_DB_PATH", BASE_DIR / "db.sqlite3"),
    }

if _db["ENGINE"].endswith("postgresql"):
    _db["CONN_MAX_AGE"] = int(os.environ.get("DB_CONN_MAX_AGE", "60"))
    _db["CONN_HEALTH_CHECKS"] = True

DATABASES = {"default": _db}
DATABASE_ENGINE = "postgresql" if _db["ENGINE"].endswith("postgresql") else "sqlite"

# --- Auth -------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "accounts.backends.EmailOrUsernameBackend",
]
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "cms:home"
LOGOUT_REDIRECT_URL = "landing"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Two-factor authentication
TOTP_ISSUER = os.environ.get("TOTP_ISSUER", "CloudMercury")
# Two-factor sign-in is switched on/off in the dashboard (Security page), not here.

# Cloudflare Turnstile. The defaults are Cloudflare's official *test* keys
# (they always pass). Replace them with your real keys in production.
TURNSTILE_SITE_KEY = os.environ.get("TURNSTILE_SITE_KEY", "1x00000000000000000000AA")
TURNSTILE_SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY", "1x0000000000000000000000000000000AA")
TURNSTILE_ENABLED = env_bool("TURNSTILE_ENABLED", True)

# --- Email ------------------------------------------------------------------
EMAIL_BACKEND = os.environ.get(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend"
    if os.environ.get("EMAIL_HOST_PASSWORD")
    else "django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "CloudMercury <cloudinovater@gmail.com>")
CONTACT_INBOX = os.environ.get("CONTACT_INBOX", "cloudinovater@gmail.com")

# --- Security hardening (active when DEBUG is off) --------------------------
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 60 * 60 * 8

# --- i18n -------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Lisbon"
USE_I18N = True
USE_TZ = True

# --- Static -----------------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"   # filled by `python manage.py collectstatic`

# WhiteNoise serves the collected static files (CSS, JS, logos) directly from Django,
# compressed and with long cache headers. It switches on automatically when installed.
WHITENOISE_INSTALLED = find_spec("whitenoise") is not None
if WHITENOISE_INSTALLED:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
    }
    WHITENOISE_MANIFEST_STRICT = False   # don't crash if a file is missing from the manifest

# Uploaded files (logos from the dashboard)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
