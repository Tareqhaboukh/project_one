from flask import Blueprint
from .user_api import user_blueprint

api_blueprints = [user_blueprint]

__all__ = ['user_blueprints']