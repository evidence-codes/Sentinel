from functools import wraps
from flask import request, jsonify, g
from bson import ObjectId
import jwt
from . import mongo

def jwt_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, 'bd0467ad425dd8508a78619a393502584d9aa6b2', algorithms=['HS256'])
            user_id = data['user_id']
            user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if not user_data:
                raise Exception('User not found')
            g.current_user = user_data  # Set the current_user
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'message': str(e)}), 401
        return f(*args, **kwargs)
    return decorated_function

def roles_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'current_user' not in g:
                return jsonify({'message': 'User not authenticated'}), 401

            user_roles = g.current_user.get('access', [])
            if 'admin' in user_roles or any(role in user_roles for role in roles):
                return f(*args, **kwargs)
            else:
                return jsonify({'message': 'Access denied: insufficient permissions'}), 403
        return decorated_function
    return wrapper
