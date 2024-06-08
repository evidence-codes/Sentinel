from . import auth
from flask import request, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Trade
from .. import mongo, bcrypt
import jwt
from app.jwt_utils import jwt_required

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
    print('User data:', user_data)
    
    if user_data and bcrypt.check_password_hash(user_data['password'], password):
        user = User(user_data)
        login_user(user)
        user_data.pop('password', None)  # Remove the password field
        serialized_user_data = serialize_user_data(user_data)  # Serialize user data
        
        # Always generate a new token
        token = jwt.encode(
            {'user_id': str(user_data['_id']), 'email': str(user_data['email']), 'access': user_data['access']},
            'bd0467ad425dd8508a78619a393502584d9aa6b2',
            algorithm='HS256'
        )
        # print('Generated token:', token)

        # Force update the user document with the new access token
        result = mongo.db.users.update_one(
            {'_id': user_data['_id']},
            {'$set': {'access_token': token}},
            upsert=True
        )
        # print('Update result:', result.modified_count)

        # Return the response with the new access token
        return jsonify({'message': 'Login successful', 'user': serialized_user_data, 'access_token': token}), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401


@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    fullname = data.get('fullname')
    email = data.get('email')
    password = data.get('password')
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    access = data.get('access')
    
    if not isinstance(access, list):
        return jsonify({'message': 'Access should be a list'}), 400
    
    if mongo.db.users.find_one({'email': email}):
        return jsonify({'message': 'Email already registered'}), 400
    
    mongo.db.users.insert_one({
        'fullname': fullname,
        'email': email,
        'password': password_hash,
        'access': access
    })
    
    return jsonify({'message': 'Registration successful'}), 201

@auth.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'}), 200



