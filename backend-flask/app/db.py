from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .settings import settings
import os

db = SQLAlchemy()

def init_db(app):
    # Belt & suspenders: compute URI with multiple fallbacks
    uri = (
        settings.DATABASE_URL
        or os.environ.get("SQLALCHEMY_DATABASE_URI")
        or os.environ.get("DATABASE_URL")
        or "sqlite:///temp.db"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    Migrate(app, db)
