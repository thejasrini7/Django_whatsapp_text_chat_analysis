"""
Django settings for myproject project (RENDER).
- Parses Render DATABASE_URL (postgres) if provided
- only uses STATICFILES_DIRS when local 'static/' exists (avoids W004)
- tuned cache & session footprints for small instances
- production security flags when DEBUG=False
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import sys
from urllib.parse import urlparse, unquote

# Add the current directory to Python path to ensure modules can be found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load local .env if present
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------- Sensitive / env-driven settings ----------------
SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-7xtf^8mx%38rgf_xv&*+oqfk1zf746akl@+*vli@w2w_my49az"
)
DEBUG = os.environ.get("DEBUG", "False") == "True"

PORT = int(os.environ.get("PORT", 10000))

# Fix the ALLOWED_HOSTS to ensure Render domains are always included
_default_hosts = [
    "127.0.0.1",
    "localhost",
    "django-whatsapp-text-chat-analysis.onrender.com",
    "*.onrender.com",  # This will match any Render subdomain
]
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS")
if ALLOWED_HOSTS:
    ALLOWED_HOSTS = [h.strip() for h in ALLOWED_HOSTS.split(",") if h.strip()]
    # Always add Render domains for safety
    for host in _default_hosts:
        if host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(host)
else:
    ALLOWED_HOSTS = _default_hosts

# Ensure CSRF trusted origins include Render domains
_default_csrf = [
    "https://django-whatsapp-text-chat-analysis.onrender.com",
    "https://*.onrender.com"
]
CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS")
if CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = [u.strip() for u in CSRF_TRUSTED_ORIGINS.split(",") if u.strip()]
    # Always add Render domains for safety
    for origin in _default_csrf:
        if origin not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(origin)
else:
    CSRF_TRUSTED_ORIGINS = _default_csrf

# ---------------- Applications ----------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "chatapp.apps.ChatappConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "myproject.urls"

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
            ],
        },
    },
]

WSGI_APPLICATION = "myproject.wsgi_render.application"

# Default DB (sqlite)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Parse Render's DATABASE_URL (Postgres) if present
db_url = os.environ.get("DATABASE_URL") or os.environ.get("DATABASE_URL_PG")
if db_url:
    parsed = urlparse(db_url)
    if parsed.scheme.startswith("postgres"):
        username = unquote(parsed.username) if parsed.username else ""
        password = unquote(parsed.password) if parsed.password else ""
        host = parsed.hostname or ""
        port = parsed.port or ""
        dbname = parsed.path.lstrip("/") if parsed.path else ""
        DATABASES["default"] = {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": dbname,
            "USER": username,
            "PASSWORD": password,
            "HOST": host,
            "PORT": port,
        }

# ---------------- Password Validators ----------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------- Internationalization ----------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------- Static & Media ----------------
STATIC_URL = "/static/"
_local_static = BASE_DIR / "static"
if _local_static.exists():
    STATICFILES_DIRS = [_local_static]
else:
    STATICFILES_DIRS = []
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------- Default auto field ----------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------- Upload & Data Limits ----------------
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# ---------------- Cache & Sessions ----------------
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "memory-cache",
        "TIMEOUT": 300,
        "OPTIONS": {"MAX_ENTRIES": 1000},
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# ---------------- Security for production ----------------
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

# Additional memory optimizations for Render
USE_THOUSAND_SEPARATOR = False
USE_L10N = False
USE_TZ = False  # Simplified timezone handling to save memory
