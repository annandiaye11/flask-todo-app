from flask import render_template, redirect, url_for, request, flash, current_app, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from models import User, Task, Category
from app import db
from datetime import datetime
from sqlalchemy import or_

def init_app(app):
    # Routes principales
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/dashboard', methods=['GET', 'POST'])
    @login_required
    def dashboard():
        if request.method == 'POST':
            content = request.form['content']
            due_date_str = request.form.get('due_date', '')
            priority = int(request.form.get('priority', 2))
            category_id = request.form.get('category_id')
            
            # Conversion de la date d'échéance
            due_date = None
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                except ValueError:
                    flash('Format de date invalide. Utilisez YYYY-MM-DD.')
                    return redirect(url_for('dashboard'))
            
            task = Task(
                content=content,
                user=current_user,
                due_date=due_date,
                priority=priority
            )
            
            if category_id and category_id != '0':
                category = Category.query.get(int(category_id))
                if category and category.user_id == current_user.id:
                    task.category = category
            
            db.session.add(task)
            db.session.commit()
            return redirect(url_for('dashboard'))
        
        # Récupération des filtres
        filter_status = request.args.get('status', 'all')
        filter_priority = request.args.get('priority', 'all')
        filter_category = request.args.get('category', 'all')
        search_query = request.args.get('search', '')
        
        # Construction de la requête avec les filtres
        query = Task.query.filter_by(user=current_user)
        
        if filter_status == 'done':
            query = query.filter_by(is_done=True)
        elif filter_status == 'pending':
            query = query.filter_by(is_done=False)
        
        if filter_priority != 'all' and filter_priority.isdigit():
            query = query.filter_by(priority=int(filter_priority))
        
        if filter_category != 'all' and filter_category.isdigit():
            query = query.filter_by(category_id=int(filter_category))
        
        if search_query:
            query = query.filter(Task.content.ilike(f'%{search_query}%'))
        
        # Tri par priorité et date d'échéance
        tasks = query.order_by(Task.priority, Task.due_date.nullslast()).all()
        
        # Récupération des catégories de l'utilisateur
        categories = Category.query.filter_by(user=current_user).all()
        
        return render_template('dashboard.html', 
                              tasks=tasks, 
                              categories=categories,
                              filter_status=filter_status,
                              filter_priority=filter_priority,
                              filter_category=filter_category,
                              search_query=search_query)
    
    # Routes d'authentification
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Nom d\'utilisateur déjà utilisé.')
                return redirect(url_for('register'))
            
            user = User(username=username)
            user.set_password(password)
            
            # Créer une catégorie par défaut pour le nouvel utilisateur
            default_category = Category(name="Général", user=user)
            
            db.session.add(user)
            db.session.add(default_category)
            db.session.commit()
            
            flash('Compte créé ! Connectez-vous.')
            return redirect(url_for('login'))
        
        return render_template('register.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('dashboard'))
            
            flash('Identifiants invalides.')
            return redirect(url_for('login'))
        
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))
    
    # Routes pour gérer les tâches
    @app.route('/delete/<int:task_id>')
    @login_required
    def delete_task(task_id):
        task = Task.query.get_or_404(task_id)
        if task.user != current_user:
            flash("Action non autorisée.")
            return redirect(url_for('dashboard'))
        
        db.session.delete(task)
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    @app.route('/toggle/<int:task_id>')
    @login_required
    def toggle_task(task_id):
        task = Task.query.get_or_404(task_id)
        if task.user != current_user:
            flash("Action non autorisée.")
            return redirect(url_for('dashboard'))
        
        task.is_done = not task.is_done
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    @app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
    @login_required
    def edit_task(task_id):
        task = Task.query.get_or_404(task_id)
        if task.user != current_user:
            flash("Action non autorisée.")
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            task.content = request.form['content']
            
            due_date_str = request.form.get('due_date', '')
            if due_date_str:
                try:
                    task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                except ValueError:
                    flash('Format de date invalide. Utilisez YYYY-MM-DD.')
                    return redirect(url_for('edit_task', task_id=task.id))
            else:
                task.due_date = None
            
            task.priority = int(request.form.get('priority', 2))
            
            category_id = request.form.get('category_id')
            if category_id and category_id != '0':
                category = Category.query.get(int(category_id))
                if category and category.user_id == current_user.id:
                    task.category = category
            else:
                task.category_id = None
            
            db.session.commit()
            flash('Tâche mise à jour avec succès!')
            return redirect(url_for('dashboard'))
        
        categories = Category.query.filter_by(user=current_user).all()
        return render_template('edit_task.html', task=task, categories=categories)
    
    # Routes pour gérer les catégories
    @app.route('/categories', methods=['GET', 'POST'])
    @login_required
    def manage_categories():
        if request.method == 'POST':
            name = request.form['name']
            if name.strip():
                category = Category(name=name, user=current_user)
                db.session.add(category)
                db.session.commit()
                flash('Catégorie ajoutée!')
            else:
                flash('Le nom de la catégorie ne peut pas être vide.')
        
        categories = Category.query.filter_by(user=current_user).all()
        return render_template('categories.html', categories=categories)
    
    @app.route('/categories/delete/<int:category_id>')
    @login_required
    def delete_category(category_id):
        category = Category.query.get_or_404(category_id)
        if category.user != current_user:
            flash("Action non autorisée.")
            return redirect(url_for('manage_categories'))
        
        # Vérifier si c'est la dernière catégorie de l'utilisateur
        if Category.query.filter_by(user=current_user).count() <= 1:
            flash("Vous devez conserver au moins une catégorie.")
            return redirect(url_for('manage_categories'))
        
        # Mettre à jour les tâches associées à cette catégorie
        default_category = Category.query.filter_by(user=current_user).first()
        for task in category.tasks:
            task.category = default_category
        
        db.session.delete(category)
        db.session.commit()
        flash('Catégorie supprimée!')
        return redirect(url_for('manage_categories'))