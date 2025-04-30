from flask import Blueprint, redirect, render_template, session, request, jsonify, flash
from services.firebase_service import db
from firebase_admin import firestore


dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
def dashboard():
    if 'user_id' not in session or 'user_email' not in session:
        flash("Please log in first.", "danger")
        return redirect('/login')

    user_email = session['user_email']

    try:
        # Fetch admin document by email
        admin_docs = db.collection('admins').where('email', '==', user_email).limit(1).get()
        if not admin_docs:
            flash("Admin record not found.", "danger")
            return redirect('/login')

        admin_data = admin_docs[0].to_dict()
        ward = admin_data.get('ward')

        if not ward:
            flash("Ward not assigned to your account.", "danger")
            return redirect('/login')

        # Save ward in session
        session['ward'] = ward

        # Fetch issues for this ward
        issues_query = db.collection('issues').where('ward', '==', ward).stream()
        issues = []
        for doc in issues_query:
            issue = doc.to_dict()
            issue['id'] = doc.id
            issues.append(issue)

        return render_template('dashboard.html', issues=issues)

    except Exception as e:
        flash(f"Error loading dashboard: {e}", "danger")
        return redirect('/login')

@dashboard_bp.route('/update-status/<issue_id>', methods=['POST'])
def update_status(issue_id):
    data = request.get_json()
    new_status = data.get('status')

    try:
        db.collection('issues').document(issue_id).update({'status': new_status})
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500
    
@dashboard_bp.route('/update-description/<issue_id>', methods=['POST'])
def update_description(issue_id):
    data = request.get_json()
    description_update = data.get('description_update')

    if not description_update:
        return jsonify(success=False, error="Description update is missing."), 400

    try:
        issue_ref = db.collection('issues').document(issue_id)

        # Add a new document to the "updates" subcollection under the issue
        update_data = {
            'message': description_update,
            'timestamp': firestore.SERVER_TIMESTAMP,
            'updated_by': session.get('user_email', 'unknown')
        }

        issue_ref.collection('updates').add(update_data)

        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500


