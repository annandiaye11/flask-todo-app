import os
from datetime import datetime

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///todolist.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def now():
        return datetime.now()

def init_app(app):
    # Rendre la fonction now disponible dans les templates
    app.jinja_env.globals.update(now=Config.now)