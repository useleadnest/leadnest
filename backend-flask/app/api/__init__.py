"""
API Blueprint for LeadNest Launch Multiplier.
"""

from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api')

# Import routes to register them
from . import onboarding, roi

__all__ = ['api']
