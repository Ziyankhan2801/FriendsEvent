from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "change-this-secret-key"
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "website",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ✅ BUSINESS SETTINGS
BUSINESS_NAME = "Friends Events Decorative"
BUSINESS_PHONE = "+919970147735"
BUSINESS_CITY = "Chopda"


# ✅ EMAIL SETTINGS (Gmail SMTP + App Password)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = "friendseventsdecor@gmail.com"
EMAIL_HOST_PASSWORD = "nmgqtihlcaehkdvg"

OWNER_EMAIL = "umerkhan708670@gmail.com"
DEFAULT_FROM_EMAIL = "Friends Events <friendseventsdecor@gmail.com>"


ADVANCE_PERCENT = 30  # 30% advance
UPI_ID = "9021520686@axl"
BUSINESS_NAME = "Friends Events Decorative"
BUSINESS_PHONE = "+919970147735"


BUSINESS_LOGO = BASE_DIR / "static" / "logo.png"


import os
import dj_database_url



# ==============================
# ✅ RENDER DEPLOY SETTINGS
# ==============================

DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",") if os.getenv("ALLOWED_HOSTS") else ["*"]

CSRF_TRUSTED_ORIGINS = []
if os.getenv("CSRF_TRUSTED_ORIGINS"):
    CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS").split(",")

# ✅ Database (Render Postgres)
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASES["default"] = dj_database_url.parse(DATABASE_URL)

# ✅ Static files (WhiteNoise)
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"



# ==============================
# ✅ CLOUDINARY MEDIA STORAGE
# ==============================
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")

if CLOUDINARY_URL:
    INSTALLED_APPS += ["cloudinary", "cloudinary_storage"]

    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
