from . import predict
import requests
from flask import request, jsonify
import warnings
warnings.filterwarnings("ignore")
import pickle
import joblib
import numpy as np
import pandas as pd
import os
from app.models import Trade
from .. import mongo

# Construct the path to the model.pkl file
current_dir = os.path.dirname(__file__)
preprocessor_path = os.path.join(current_dir, '..', 'data', '2preprocessor.pkl')
model_path = os.path.join(current_dir, '..', 'data', '2model.pkl')

print(pickle.format_version)

# Load the preprocessor with error handling
try:
    with open(preprocessor_path, 'rb') as processor_file:
        preprocessor = joblib.load(processor_file)
except FileNotFoundError:
    print(f"Preprocessor file not found at {preprocessor_path}")
    preprocessor = None
except Exception as e:
    print(f"An error occurred while loading the preprocessor: {e}")
    preprocessor = None
    
# Load the model with error handling
try:
    with open(model_path, 'rb') as model_file:
        model = pickle.load(model_file)
except FileNotFoundError:
    print(f"Model file not found at {model_path}")
    model = None
except Exception as e:
    print(f"An error occurred while loading the model: {e}")
    model = None    
    

#Trade-in value prediction route    
@predict.route('/price_model', methods=['POST'])
def price_predict():
    data = request.get_json()
    region = data.get('region')
    device_RAM = data.get('device_RAM')
    device_storage = data.get('device_storage')
    new_price_dollars = data.get('new_price_dollars')
    device_category = data.get('device_category')
    condition_category = data.get('condition_category')
    months_used = data.get('months_used')
    
    new_data_dict = {
        'region': [region],
        'device_RAM': [device_RAM],
        'device_storage': [device_storage],
        'new_price_dollars': [new_price_dollars],
        'device_category': [device_category],
        'condition_category': [condition_category],
        'months_used': [months_used]
    }
    
    # Convert new_data into a DataFrame
    new_data_df = pd.DataFrame(new_data_dict)
    
    # Preprocess the new data using the loaded preprocessing steps first before using the model on it
    preprocessed_data = preprocessor.transform(new_data_df)
    
    # Make predictions using the trained model
    # predicted_trade_in_price = model.predict(preprocessed_data)[0]
    predicted_trade_in_price = model.predict(preprocessed_data)[0]
    
    
    # Calculate the preowned value of the device
    preowned_value = (0.3 * predicted_trade_in_price) + predicted_trade_in_price
    
    # return jsonify({
    #     'predicted_trade_in_price': predicted_trade_in_price,
    #     'preowned_value': preowned_value})
    
    
    url = 'https://v6.exchangerate-api.com/v6/f50628742f57bef260de9dba/latest/NGN'
    
    # Making our request
    response = requests.get(url)
    exchange_data = response.json()
    exchange_rate = exchange_data['conversion_rates']['USD']
    
    dollar_price = convert_to_dollar(new_price_dollars, exchange_rate)
    
    
    # Handle cases where the exchange API request fails
    if response.status_code != 200 or 'conversion_rates' not in exchange_data:
        return jsonify({'message': 'Failed to retrieve exchange rates'}), 500
    
    # return jsonify({'message': dollar_price})
    # return jsonify({'message': exchange_data})
    
    # arr = np.array([[manufacturer, storage, dollar_price]])
    # prediction = price_model.predict(arr)
    
    # Convert predicted price in dollar to naira
    naira_price = convert_to_naira(predicted_trade_in_price, exchange_rate)
    preowned_naira = convert_to_naira(preowned_value, exchange_rate)
    
    
    
    # mongo.db.trades.insert_one({
    #     'manufacturer': manufacturer,
    #     'storage': storage,
    #     'price': price,
    #     'prediction': naira_price
    # })
    
    return jsonify({'message': 'Prediction successful', 'predicted_trade_in_price': naira_price, 'preowned_value': preowned_naira})


def convert_to_dollar(naira, rate):
    return naira * rate

def convert_to_naira(dollar, rate):
    return dollar / rate


