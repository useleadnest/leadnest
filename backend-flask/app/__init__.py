from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from .settings import settings
from .db import init_db
from . import middleware
from redis import Redis
import os

# Global limiter instance
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"]
)

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY=settings.JWT_SECRET)

    # Trust proxy headers for HTTPS/host detection (Render/Cloudflare)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)
    app.config["PREFERRED_URL_SCHEME"] = "https"

    # CORS - explicit configuration for production
    allowed_origins = [
        "https://useleadnest.com",
        "https://www.useleadnest.com",
    ]
    
    CORS(
        app,
        resources={r"/api/*": {"origins": allowed_origins}},
        supports_credentials=False,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        expose_headers=["Authorization"],
        max_age=86400,
    )

    @app.after_request
    def add_cors_cache_headers(resp):
        # Some proxies strip max-age if not repeated
        if resp.headers.get("Access-Control-Allow-Origin"):
            resp.headers.setdefault("Access-Control-Max-Age", "86400")
        return resp

    # Rate limiting
    limiter.init_app(app)

    # DB
    init_db(app)

    # ✅ Ensure models are imported so Flask-Migrate/Alembic sees them
    from . import models

    # ✅ Seed default Business to avoid foreign-key errors
    from .models import db, Business

    with app.app_context():
        try:
            if not Business.query.first():
                b = Business(name="Default Business", niche="general", owner_email="owner@example.com")
                db.session.add(b)
                db.session.commit()
        except Exception:
            # Tables might not exist yet
            pass

    # Redis connection for RQ
    try:
        redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        app.redis = Redis.from_url(redis_url)
    except Exception:
        app.redis = None

    # Middleware
    app.before_request(middleware.before_request)
    app.after_request(middleware.after_request)

    # ✅ Import API after limiter is defined to avoid circular import
    from .api import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    # Root-level health routes (not under /api prefix)
    @app.route("/")
    def root():
        return {"status": "healthy", "service": "leadnest-api", "version": "1.0.0"}

    @app.route("/health")
    def health():
        return {"status": "healthy"}

    @app.route("/healthz")
    def healthz():
        return {"status": "healthy"}

    @app.route("/readyz") 
    def readyz():
        return {"status": "ready"}

    return app
