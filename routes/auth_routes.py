from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from firebase_admin import auth
from services.firebase_service import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            # Check if the email is in the admins collection
            admins_ref = db.collection('admins').where('email', '==', email).stream()

            admin_doc = None
            for doc in admins_ref:
                admin_doc = doc
                break

            if not admin_doc:
                flash("Access denied: You are not authorized to access the admin panel.", "danger")
                return redirect(url_for('auth.login'))

            admin_data = admin_doc.to_dict()
            if admin_data.get('password') != password:
                flash("Incorrect password.", "danger")
                return redirect(url_for('auth.login'))

            # Proceed with Firebase auth and user info
            user = auth.get_user_by_email(email)
            name = db.collection('users').document(user.uid).get().get('name')

            session['user_id'] = user.uid
            session['user_email'] = email
            session['name'] = name
            session['ward'] = admin_data.get('ward') 

            flash("Login successful!", "success")
            return redirect(url_for('dashboard.dashboard'))

        except Exception as e:
            flash(f"Login failed: {e}", "danger")

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
