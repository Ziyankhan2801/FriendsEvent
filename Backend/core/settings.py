from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# =====================================================
# SECURITY
# =====================================================

SECRET_KEY = os.getenv("SECRET_KEY", "unsafe-secret-key")

DEBUG = os.getenv("DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    "friendsevent.onrender.com",
    ".onrender.com",
    "friendseventsdecor.netlify.app",
    "localhost",
    "127.0.0.1",
]

CSRF_TRUSTED_ORIGINS = [
    "https://friendsevent.onrender.com",
    "https://friendseventsdecor.netlify.app",
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True


# =====================================================
# APPLICATIONS
# =====================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "website",
]


# =====================================================
# MIDDLEWARE
# =====================================================

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # MUST FIRST
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]


# =====================================================
# CORS SETTINGS (FINAL FIX)
# =====================================================

CORS_ALLOWED_ORIGINS = [
    "https://friendseventsdecor.netlify.app",
]

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True


# =====================================================
# URL / WSGI
# =====================================================

ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"


# =====================================================
# TEMPLATES
# =====================================================

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


# =====================================================
# DATABASE (SAFE VERSION)
# =====================================================

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.strip() != "":
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# =====================================================
# STATIC / MEDIA
# =====================================================

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ======================
# EMAIL (PRODUCTION SAFE)
# ======================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 5 # 🔥 IMPORTANT (prevents worker hang)

EMAIL_HOST_USER = "friendseventsdecor@gmail.com"
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = "Friends Events <friendseventsdecor@gmail.com>"
OWNER_EMAIL = "umerkhan708670@gmail.com"



# =====================================================
# BUSINESS
# =====================================================

BUSINESS_NAME = "Friends Events Decorative"
UPI_ID = "9021520686@axl"
BUSINESS_CITY = "Chopda"

# =====================================================
# CLOUDINARY
# =====================================================

CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")

if CLOUDINARY_URL:
    INSTALLED_APPS += [
        "cloudinary",
        "cloudinary_storage",
    ]
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
