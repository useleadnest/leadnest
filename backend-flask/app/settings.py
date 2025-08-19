import os

class Settings:
    # Accept either name; default to local sqlite for dev
    _raw_database_url = (
        os.environ.get("SQLALCHEMY_DATABASE_URI")
        or os.environ.get("DATABASE_URL")
        or "sqlite:///temp.db"
    )
    
    # Convert postgresql:// to postgresql+psycopg:// to use psycopg3 instead of psycopg2
    if _raw_database_url.startswith("postgresql://"):
        DATABASE_URL = _raw_database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    else:
        DATABASE_URL = _raw_database_url
    JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-in-production")
    CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "*").split(",") if o.strip()]
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    PORT = int(os.environ.get("PORT", 8000))

settings = Settings()
