from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Użytkownik o takiej nazwie już istnieje.', 'danger')
            return redirect(url_for('auth.register'))
            
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Konto stworzone pomyślnie! Możesz się zalogować.', 'success')
            return redirect(url_for('auth.login'))
        except Exception:
            db.session.rollback()
            flash('Wystąpił błąd podczas rejestracji.', 'danger')
            
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('repos.index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f'Witaj z powrotem, {username}!', 'success')
            return redirect(url_for('repos.index'))
        else:
            flash('Błędne dane logowania.', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Wylogowano pomyślnie.', 'info')
    return redirect(url_for('auth.login')) # Dodano auth.