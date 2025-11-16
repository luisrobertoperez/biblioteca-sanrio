from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Note
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_clave_secreta_super_segura'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensiones
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# RUTAS PRINCIPALES
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verificar si el usuario ya existe
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe')
            return render_template('register.html')
        
        # Crear nuevo usuario
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registro exitoso. Ahora puedes iniciar sesión.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    notes = Note.query.filter_by(user_id=current_user.id).all()
    themes = ['hello-kitty-theme', 'my-melody-theme', 'kuromi-theme', 'cinnamoroll-theme']
    return render_template('dashboard.html', notes=notes, themes=themes)

@app.route('/add_note', methods=['GET', 'POST'])
@login_required
def add_note():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        if not title:
            flash('El título es requerido')
            return render_template('add_note.html')
        
        new_note = Note(title=title, content=content, user_id=current_user.id)
        db.session.add(new_note)
        db.session.commit()
        
        flash('Nota agregada exitosamente')
        return redirect(url_for('dashboard'))
    
    return render_template('add_note.html')

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    notes = []
    if request.method == 'POST':
        search_term = request.form['search_term']
        notes = Note.query.filter(
            Note.user_id == current_user.id,
            Note.title.contains(search_term)
        ).all()
    
    return render_template('search.html', notes=notes)

# Inicializar la base de datos
def init_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)