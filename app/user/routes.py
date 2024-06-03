from . import user
from flask import request, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import User, Trade
from .. import mongo, bcrypt
import jwt
from app.jwt_utils import jwt_required



@user.route('/get-predictions', methods=['GET'])
@jwt_required
def get_predictions():
    # Extract the user ID from the JWT token
    access_token = request.headers.get('Authorization')
    decoded_token = jwt.decode(access_token, 'bd0467ad425dd8508a78619a393502584d9aa6b2', algorithms=['HS256'])
    user_id = decoded_token['user_id']
    
    # Find all predictions with the specified user_id
    predictions = mongo.db.trades.find({'user_id': user_id}).sort('created_at', 1)
    
    # Convert the cursor to a list of dictionaries
    predictions_list = []
    for prediction in predictions:
        prediction['_id'] = str(prediction['_id'])  # Convert ObjectId to string
        predictions_list.append(prediction)
    
    return jsonify(predictions_list), 200