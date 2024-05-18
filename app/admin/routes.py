from . import admin
from flask import request, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Admin 
from .. import mongo, bcrypt


# admin = Blueprint('admin', __name__)

def serialize_doc(doc):
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

@admin.route('/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    admin_data = mongo.db.admins.find_one({'email': email})
    
    if admin_data and bcrypt.check_password_hash(admin_data['password'], password):
        admin = Admin(admin_data)
        login_user(admin)
        admin_data.pop('password', None)
        return jsonify({'message': 'Admin login successful', 'admin': serialize_doc(admin_data)}), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401
    
    
    
@admin.route('/register', methods=['POST'])
def admin_register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    if mongo.db.admins.find_one({'email': email}):
        return jsonify({'message': 'Email already registered'}), 400
    
    mongo.db.admins.insert_one({
        'username': username,
        'email': email,
        'password': password_hash
    })
    
    return jsonify({'message': 'Admin created successfully'}), 201