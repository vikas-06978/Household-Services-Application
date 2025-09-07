import os
from pathlib import Path

# Defining folders for database and report files
project_dir = Path(__file__).resolve().parent
db_dir = project_dir / "database"
reports_dir = project_dir / "user_reports"


if not db_dir.exists():
    db_dir.mkdir(parents=True)

if not reports_dir.exists():
    reports_dir.mkdir(parents=True)

class ServigoConfig:
    # Hidden secete key will be here
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_secret_key")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET", "dev_jwt_key")

    # using local SQLite here 
    DB_FILE = "database.db"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DB_PATH", f"sqlite:///{db_dir / DB_FILE}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CORS_ALLOWED_ORIGINS = [
        "http://localhost:8080",
        "https://servigo.com"
    ]

    # Keep Debuging mode on for testing
    DEBUG = True

    # Email config — works with Mailhog in local setup
    MAIL_SERVER = "localhost"
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_SUPPRESS_SEND = False
    MAIL_DEFAULT_SENDER = "servigo@gmail.com"

    # Celery with Redis broker for async tasks
    CELERY_BROKER_URL = os.environ.get("REDIS_BROKER", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND = os.environ.get("REDIS_RESULT_BACKEND", "redis://localhost:6379/0")
    CELERY_IMPORTS = ["tasks"]

    # Redis caching config
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = os.environ.get("REDIS_CACHE_URL", "redis://localhost:6379/1")
    CACHE_DEFAULT_TIMEOUT = 300

    # File path for storing exported reports
    REPORTS_STORAGE = str(reports_dir)
