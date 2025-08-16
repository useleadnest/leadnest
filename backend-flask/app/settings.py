import os

class Settings:
    # Accept either name; default to local sqlite for dev
    DATABASE_URL = (
        os.environ.get("SQLALCHEMY_DATABASE_URI")
        or os.environ.get("DATABASE_URL")
        or "sqlite:///temp.db"
    )
    JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-in-production")
    CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "*").split(",") if o.strip()]
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    PORT = int(os.environ.get("PORT", 8000))

settings = Settings()
