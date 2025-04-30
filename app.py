from flask import Flask, Response, render_template, request, redirect, url_for, flash, session, jsonify
from flask_cors import cross_origin
from dotenv import load_dotenv
import os
from services.firebase_service import init_firebase
import make_maps

# Initialize Firebase
init_firebase()

from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from services.firebase_service import db



# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['db'] = db
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Register Blueprints for authentication and dashboard routes
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/map/<category_name>')
def show_map(category_name):
    db = app.config['db']  # Firebase DB initialized somewhere before running
    map_html = make_maps.generate_category_map(db, category_name)

    if map_html is None:
        return f"No data found for category: {category_name}", 404

    return Response(map_html, mimetype='text/html')



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
