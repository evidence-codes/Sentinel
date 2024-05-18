from . import predict
import requests
from flask import request, jsonify
import pickle
import numpy as np
import os
from app.models import Trade
from .. import mongo

# Construct the path to the model.pkl file
current_dir = os.path.dirname(__file__)
model_path = os.path.join(current_dir, '..', 'data', 'price_model.pkl')

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
    

#Trade-in value prediction route    
@predict.route('/price_model', methods=['POST'])
def price_predict():
    data = request.get_json()
    manufacturer = data.get('manufacturer')
    storage = data.get('storage')
    price = data.get('price')
    
    url = 'https://v6.exchangerate-api.com/v6/f50628742f57bef260de9dba/latest/NGN'
    
    # Making our request
    response = requests.get(url)
    exchange_data = response.json()
    exchange_rate = exchange_data['conversion_rates']['USD']
    
    dollar_price = convert_to_dollar(price, exchange_rate)
    
    
    # Handle cases where the exchange API request fails
    if response.status_code != 200 or 'conversion_rates' not in exchange_data:
        return jsonify({'message': 'Failed to retrieve exchange rates'}), 500
    
    # return jsonify({'message': dollar_price})
    # return jsonify({'message': exchange_data})
    
    arr = np.array([[manufacturer, storage, dollar_price]])
    prediction = price_model.predict(arr)
    
    # Convert predicted price in dollar to naira
    naira_price = convert_to_naira(prediction, exchange_rate)
    
    
    
    mongo.db.trades.insert_one({
        'manufacturer': manufacturer,
        'storage': storage,
        'price': price,
        'prediction': naira_price
    })
    
    return jsonify({'message': 'Prediction successful', 'prediction': naira_price})


def convert_to_dollar(naira, rate):
    return naira * rate

def convert_to_naira(dollar, rate):
    return dollar / rate


