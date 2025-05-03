from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Initialisation des extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'

# Créer l'application
def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Assurer que la clé secrète existe
    if app.config['SECRET_KEY'] == 'dev-secret-key':
        app.config['SECRET_KEY'] = os.urandom(24).hex()
    
    db.init_app(app)
    login_manager.init_app(app)
    
    # Définir user_loader
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # Importer et initialiser les routes et config
    with app.app_context():
        from routes import init_app as init_routes
        from config import init_app as init_config
        
        init_routes(app)
        init_config(app)
        
        # Créer les tables si elles n'existent pas
        db.create_all()
    
    return app

# Créer une instance de l'application
app = create_app()

# Lancer l'application si exécuté directement
if __name__ == '__main__':
    app.run(debug=True)