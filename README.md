# Flask Todo App

Une application de gestion de tâches développée avec Flask, permettant aux utilisateurs de créer, organiser et suivre leurs tâches quotidiennes.

## 📋 Fonctionnalités

- Création et gestion de tâches
- Catégorisation des tâches
- Définition de priorités (haute, moyenne, basse)
- Dates d'échéance pour les tâches
- Filtrage et recherche de tâches
- Interface intuitive et responsive

## 🛠️ Technologies utilisées

- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Base de données**: SQLite
- **Frontend**: HTML, Tailwind CSS, JavaScript
- **Sécurité**: Werkzeug pour le hachage des mots de passe

## 🚀 Installation et démarrage

```bash
# Cloner le repository
git clone https://github.com/annandiaye11/flask-todo-app.git
cd flask-todo-app

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Initialiser la base de données
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Lancer l'application
python run.py
```

## 🔒 Sécurité

- Chaque utilisateur peut créer un compte et se connecter
- Mots de passe hachés avec Werkzeug (generate_password_hash, check_password_hash)
- Les sessions sont gérées avec une SECRET_KEY (dans config.py)

## 🎨 Design

- Utilise Tailwind CSS via CDN (aucune compilation nécessaire)
- Design responsive, épuré et moderne
- Possibilité d'ajouter des icônes avec Heroicons ou FontAwesome

## 🙋‍♀️ Développé par

Projet réalisé par **Anna Ndiaye** dans le cadre de l'examen de Flask 💻.

GitHub: [annandiaye11](https://github.com/annandiaye11)

## 📝 Licence

MIT
