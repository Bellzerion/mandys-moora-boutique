from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models.user import User
from app.forms.auth import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
        
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(fullname=form.fullname.data, email=form.email.data.lower(), role='customer')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', title='Register', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Re-route based on roles
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'staff':
            return redirect(url_for('staff.products'))
        return redirect(url_for('main.home'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.fullname}!', 'success')
            
            if user.role == 'admin':
                return redirect(next_page or url_for('admin.dashboard'))
            elif user.role == 'staff':
                return redirect(next_page or url_for('staff.products'))
            return redirect(next_page or url_for('main.home'))
        else:
            flash('Login unsuccessful. Check your credentials.', 'danger')
            
    return render_template('auth/login.html', title='Login', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.home'))
