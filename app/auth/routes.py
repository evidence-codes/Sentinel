from . import auth
from flask import request, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User 
from .. import mongo, bcrypt

# auth = Blueprint('auth', __name__)

from bson import ObjectId

def serialize_user_data(user_data):
    # Convert ObjectId to string
    if '_id' in user_data:
        user_data['_id'] = str(user_data['_id'])
    return user_data

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user_data = mongo.db.users.find_one({'email': email})
    
    if user_data and bcrypt.check_password_hash(user_data['password'], password):
        user = User(user_data)
        login_user(user)
        user_data.pop('password', None)  # Remove the password field
        serialized_user_data = serialize_user_data(user_data)  # Serialize user data
        return jsonify({'message': 'Login successful', 'user': serialized_user_data}), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401



@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    if mongo.db.users.find_one({'email': email}):
        return jsonify({'message': 'Email already registered'}), 400
    
    mongo.db.users.insert_one({
        'username': username,
        'email': email,
        'password': password_hash
    })
    
    return jsonify({'message': 'Registration successful'}), 201

@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200