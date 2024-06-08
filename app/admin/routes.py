from . import admin
from flask import request, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Admin, Trade
from .. import mongo, bcrypt
from bson import ObjectId


# admin = Blueprint('admin', __name__)

def serialize_doc(doc):
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    return doc

@admin.route('/login', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        admin_data = mongo.db.admins.find_one({'email': email})
        
        if admin_data and bcrypt.check_password_hash(admin_data['password'], password):
            admin = Admin(admin_data)
            login_user(admin)
            admin_data.pop('password', None)
            admin_access = 'admin'
            return jsonify({'message': 'Admin login successful', 'admin': serialize_doc(admin_data), 'access': admin_access}), 200
        else:
            return jsonify({'message': 'Invalid email or password'}), 401
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error during admin login: {e}")
        return jsonify({'message': 'An error occurred during login'}), 500
    
    
@admin.route('/register', methods=['POST'])
def admin_register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    if mongo.db.admins.find_one({'email': email}):
        return jsonify({'message': 'Email already registered'}), 400
    
    mongo.db.admins.insert_one({
        'email': email,
        'password': password_hash
    })
    
    return jsonify({'message': 'Admin created successfully'}), 201


@admin.route('/get-all-predictions', methods=['GET'])
def get_all_predictions():
    # Fetch all documents from the 'trades' collection, sorted by 'created_at'
    predictions = mongo.db.trades.find().sort('created_at', 1)
    
    # Convert the cursor to a list of dictionaries
    predictions_list = []
    for prediction in predictions:
        prediction['_id'] = str(prediction['_id'])  # Convert ObjectId to string
        predictions_list.append(prediction)
    
    return jsonify(predictions_list), 200



@admin.route('/get-all-users', methods=['GET'])
def get_all_users():
    # Fetch all documents from the 'trades' collection, sorted by 'created_at'
    users = mongo.db.users.find().sort('created_at', 1)
    
    # Convert the cursor to a list of dictionaries
    users_list = []
    for user in users:
        user['_id'] = str(user['_id'])  # Convert ObjectId to string
        users_list.append(user)
    
    return jsonify(users_list), 200

@admin.route('/update-user/<user_id>', methods=['PATCH'])
def update_user(user_id):
    data = request.get_json()
    update_fields = {}
    
    # Collect the fields to update
    if 'fullname' in data:
        update_fields['fullname'] = data['fullname']
    if 'email' in data:
        update_fields['email'] = data['email']
    if 'access' in data:
        update_fields['access'] = data['access']
    
    # Update the user in the database
    result = mongo.db.users.update_one({'_id': ObjectId(user_id)}, {'$set': update_fields})
    
    if result.matched_count > 0:
        return jsonify({'message': 'User updated successfully!'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404

    
@admin.route('/delete-user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    # Delete the user from the database
    result = mongo.db.users.delete_one({'_id': ObjectId(user_id)})
    
    if result.deleted_count > 0:
        return jsonify({'message': 'User deleted successfully!'}), 200
    else:
        return jsonify({'message': 'User not found'}), 404   