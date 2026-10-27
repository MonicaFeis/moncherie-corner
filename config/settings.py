"""
Settings for the moncherie corner shop.

Secret values (secret key, database address, passwords) are NOT written
in this file. They are read from "environment variables":
- on your Mac they come from the .env file (never uploaded to GitHub)
- on Heroku they come from "Config Vars"
"""
import os
import sys
from pathlib import Path

import dj_database_url
from django.contrib.messages import constants as messages
from dotenv import load_dotenv

# The main project folder (the one with manage.py in it)
BASE_DIR = Path(__file__).resolve().parent.parent

# Read the .env file, if there is one
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ["SECRET_KEY"]

# DEBUG is only switched on when .env says DEBUG=True.
# On Heroku it stays off, so error pages never show secret details.
DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Our own apps
    "home",
    "accounts",
    "products",
    "cart",
    "checkout",
    "notifications",
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

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Shared pages (base.html, 404.html) live in the "templates" folder
        "DIRS": [BASE_DIR / "templates"],
        # Each app's own pages live in <app>/templates/<app>/
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "cart.context_processors.cart",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# On your Mac: a small file database (db.sqlite3).
# On Heroku: Postgres, read from the DATABASE_URL config var.
DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/Berlin"
USE_I18N = True
USE_TZ = True


# Static files: your CSS, JavaScript, logo and drawings
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files: things uploaded on the site (product images and downloads).
# Cloudinary is added later, in the products step.
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Where to send people for login, and after login and logout
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "home:index"
LOGOUT_REDIRECT_URL = "home:index"

# Django calls errors "error"; Bootstrap calls the red alert "danger"
MESSAGE_TAGS = {messages.ERROR: "danger"}


# Emails
# The web address used for links inside emails
SITE_URL = os.environ.get("SITE_URL", "http://127.0.0.1:8000")
DEFAULT_FROM_EMAIL = os.environ.get(
    "DEFAULT_FROM_EMAIL", "moncherie corner <noreply@example.com>"
)

if os.environ.get("EMAIL_HOST"):
    # A real email server is set up (on Heroku): send real emails
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = os.environ["EMAIL_HOST"]
    EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
    EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
    EMAIL_USE_TLS = True
else:
    # No email server: emails are printed in the VS Code terminal instead
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# Stripe payments (test mode). The keys live in .env, never in git.
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
STRIPE_CURRENCY = "eur"


# ---------- Deployment (Heroku) ----------
# True while "python manage.py test" runs, so tests never upload to Cloudinary
TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"

# The live web address, for example https://moncherie-corner-abc123.herokuapp.com
CSRF_TRUSTED_ORIGINS = [
    origin for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if origin
]

# Uploaded images and downloads go to Cloudinary on Heroku,
# because Heroku deletes uploaded files every time the app restarts.
USE_CLOUDINARY = bool(os.environ.get("CLOUDINARY_URL")) and not TESTING
if USE_CLOUDINARY:
    INSTALLED_APPS += ["cloudinary_storage", "cloudinary"]
    STORAGES["default"] = {"BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage"}

# Extra safety when DEBUG is off (on Heroku)
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = not TESTING
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
