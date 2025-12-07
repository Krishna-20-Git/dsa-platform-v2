from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, current_user, logout_user, login_required
from models import db, User, UserProgress # Import from your models.py
from flask_bcrypt import Bcrypt

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth_bp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if user exists
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('auth.register'))
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('register.html')

@auth_bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            
    return render_template('login.html')

@auth_bp.route("/logout")
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info') 
    return redirect(url_for('auth.login'))

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    # Calculate progress
    total_modules = 23 # You have 23 visualizers
    completed = UserProgress.query.filter_by(user_id=current_user.id).count()
    # Get distinct modules completed to avoid double counting
    distinct_completed = db.session.query(UserProgress.module_name).filter_by(user_id=current_user.id).distinct().count()
    
    progress_percent = int((distinct_completed / total_modules) * 100)
    
    history = UserProgress.query.filter_by(user_id=current_user.id).order_by(UserProgress.timestamp.desc()).limit(10).all()
    
    return render_template('dashboard.html', percent=progress_percent, count=distinct_completed, history=history)