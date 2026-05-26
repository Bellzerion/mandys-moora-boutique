from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.extensions import db
from app.models.user import User
from app.services.analytics import get_dashboard_metrics
from app.routes.decorators import role_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    metrics = get_dashboard_metrics()
    return render_template('admin/dashboard.html', metrics=metrics)

@admin_bp.route('/staff', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def staff():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email').lower()
        password = request.form.get('password')
        
        # Check duplicate
        user = User.query.filter_by(email=email).first()
        if user:
            flash('This email is already registered.', 'danger')
            return redirect(url_for('admin.staff'))
            
        new_staff = User(fullname=fullname, email=email, role='staff')
        new_staff.set_password(password)
        db.session.add(new_staff)
        db.session.commit()
        
        flash(f'Staff account for {fullname} created successfully!', 'success')
        return redirect(url_for('admin.staff'))
        
    # List all users with role 'staff' and 'admin'
    staff_members = User.query.filter(User.role.in_(['staff', 'admin'])).all()
    return render_template('admin/staff.html', staff_members=staff_members)

@admin_bp.route('/staff/delete/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_staff(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('Cannot delete administrator accounts.', 'danger')
        return redirect(url_for('admin.staff'))
        
    name = user.fullname
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Staff member {name} removed.', 'info')
    return redirect(url_for('admin.staff'))
