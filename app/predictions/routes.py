from . import predict
from flask import request, jsonify
import pickle
import numpy as np
import os

# Construct the path to the model.pkl file
current_dir = os.path.dirname(__file__)
model_path = os.path.join(current_dir, '..', 'data_model', 'price_model.pkl')

# Load the model with error handling
try:
    with open(model_path, 'rb') as model_file:
        price_model = pickle.load(model_file)
except FileNotFoundError:
    print(f"Model file not found at {model_path}")
    price_model = None
except Exception as e:
    print(f"An error occurred while loading the model: {e}")
    price_model = None
    
    
@predict.route('/price_model', methods=['POST'])
def price_predict():
    data = request.get_json()
    manufacturer = data.get('manufacturer')
    storage = data.get('storage')
    price = data.get('price')
    
    arr = np.array([[manufacturer, storage, price]])
    prediction = price_model.predict(arr)
    
    return jsonify({'message': 'Prediction successful', 'prediction': prediction})





