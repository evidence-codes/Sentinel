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
from app.models import Trade, User
from .. import mongo
from app.jwt_utils import jwt_required, roles_required
import jwt
from datetime import datetime
import io
from flask import send_file

# Construct the path to the model.pkl file
current_dir = os.path.dirname(__file__)
preprocessor_path = os.path.join(current_dir, '..', 'data', '2preprocessor.pkl')
model_path = os.path.join(current_dir, '..', 'data', '2model.pkl')
sap_preprocessor_path = os.path.join(current_dir, '..', 'data', 'sap_preprocessor.pkl')
sap_model_path = os.path.join(current_dir, '..', 'data', 'sap_model.pkl')
sld_preprocessor_path = os.path.join(current_dir, '..', 'data', '1sld_preprocessor.pkl')
sld_model_path = os.path.join(current_dir, '..', 'data', '1sld_model.pkl')

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
    
try:
    with open(sap_preprocessor_path, 'rb') as sap_model_file:
        sap_preprocessor = pickle.load(sap_model_file)
except FileNotFoundError:
    print(f"SAP preprocessor file not found at {sap_preprocessor_path}")        
    sap_preprocessor = None
except Exception as e:
    print(f"An error occured while loading the preprocessor: {e}")        
    sap_preprocessor = None    
        
try:
    with open(sap_model_path, 'rb') as sap_model_file:
        sap_model = pickle.load(sap_model_file)
except FileNotFoundError:
    print(f"SAP model file not found at {sap_model_path}")
    sap_model = None
except Exception as e:
    print(f"An error occured while loading the model: {e}")
    sap_model = None
    
    
try:
    with open(sld_preprocessor_path, 'rb') as sld_model_file:
        sld_preprocessor = pickle.load(sld_model_file)
except FileNotFoundError:
    print(f"SLD preprocessor file not found at {sld_preprocessor_path}")        
    sld_preprocessor = None
except Exception as e:
    print(f"An error occured while loading the preprocessor: {e}")        
    sld_preprocessor = None    
        
try:
    with open(sld_model_path, 'rb') as sld_model_file:
        sld_model = pickle.load(sld_model_file)
except FileNotFoundError:
    print(f"SLD model file not found at {sld_model_path}")
    sld_model = None
except Exception as e:
    print(f"An error occured while loading the model: {e}")
    sld_model = None    
    
    

#Trade-in value prediction route    
@predict.route('/price_model', methods=['POST'])
@jwt_required
def price_predict():
    data = request.get_json()
    region = data.get('region')
    device_RAM = data.get('device_RAM')
    device_storage = data.get('device_storage')
    new_device_price = data.get('new_device_price')
    device_category = data.get('device_category')
    condition_category = data.get('condition_category')
    months_used = data.get('months_used')
    
    # Ensure all required fields are provided
    required_fields = ['region', 'device_RAM', 'device_storage', 'new_device_price', 'device_category', 'condition_category', 'months_used']
    if not all(field in data for field in required_fields):
        return jsonify({'message': f'Missing required fields. Required fields are: {required_fields}'}), 400
    
    # Get exchange rate
    url = 'https://v6.exchangerate-api.com/v6/f50628742f57bef260de9dba/latest/NGN'
    response = requests.get(url)
    if response.status_code != 200 or 'conversion_rates' not in response.json():
        return jsonify({'message': 'Failed to retrieve exchange rates'}), 500
    
    exchange_data = response.json()
    exchange_rate = exchange_data['conversion_rates']['USD']

    # Convert new_price from Naira to dollars
    new_price_dollars = convert_to_dollar(new_device_price, exchange_rate)
    print(new_price_dollars)

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
    
    # Preprocess the new data using the loaded preprocessing steps
    preprocessed_data = preprocessor.transform(new_data_df)
    
    # Make predictions using the trained model
    predicted_trade_in_price = model.predict(preprocessed_data)[0]
    
    result = mongo.db.devices.find_one({'category': device_category})
    profit_percent = int(result['profit_percent']) / 100
    # Calculate the preowned value of the device
    preowned_value = (profit_percent * predicted_trade_in_price) + predicted_trade_in_price
    
    # Convert predicted price in dollar to naira
    naira_price = convert_to_naira(predicted_trade_in_price, exchange_rate)
    preowned_naira = convert_to_naira(preowned_value, exchange_rate)
    
    # Extract the user ID from the JWT token
    access_token = request.headers.get('Authorization')
    decoded_token = jwt.decode(access_token, 'bd0467ad425dd8508a78619a393502584d9aa6b2', algorithms=['HS256'])
    user_id = decoded_token['user_id']
    user_email = decoded_token['email']
    
    user_data = mongo.db.users.find_one({'email': user_email})
    user_name = user_data['fullname']
    
    mongo.db.trades.insert_one({
        'user_id': user_id,
        'user_name': user_name,
        'region': region,
        'device_RAM': device_RAM,
        'device_storage': device_storage,
        'new_price': new_device_price,  # Save the new_price in Naira
        'device_category': device_category,
        'condition_category': condition_category,
        'months_used': months_used,
        'predicted_trade_in_price': naira_price,
        'preowned_value': preowned_naira,
        'created_at': datetime.utcnow()  # Add timestamp
    })
    
    return jsonify({'message': 'Prediction successful', 'predicted_trade_in_price': naira_price, 'preowned_value': preowned_naira})



def convert_to_dollar(naira, rate):
    return naira * rate

def convert_to_naira(dollar, rate):
    return dollar / rate



@predict.route('/insurance_model', methods=['POST'])
def insurance_predict():
    data = request.get_json()
    device_price = data.get('device_price')
    device_brand = data.get('device_brand')
    device_ram = data.get('device_ram')
    device_storage = data.get('device_storage')
    screen_price = data.get('screen_price')

    # Create a dictionary containing the data received from the form
    sld_data = {
        'device_price': [device_price],
        'device_brand': [device_brand],
        'device_ram': [device_ram],
        'device_storage': [device_storage],
        'screen_price': [screen_price]
    }
    
    sap_data = {
        'device_price': [device_price],
        'device_brand': [device_brand],
        'device_ram': [device_ram],
        'device_storage': [device_storage]
    }

    # Convert new_data into a DataFrame
    sld_new_data_df = pd.DataFrame(sld_data)
    sap_new_data_df = pd.DataFrame(sap_data)

    # Preprocess the new data using the loaded preprocessing steps
    sap_preprocessed_data = sap_preprocessor.transform(sap_new_data_df)
    sld_preprocessed_data = sld_preprocessor.transform(sld_new_data_df)

    # Make predictions using the trained model
    sap_predictions = sap_model.predict(sap_preprocessed_data)
    sld_predictions = sld_model.predict(sld_preprocessed_data)
    
    mongo.db.insurances.insert_one({
        'device_price': device_price,
        'device_brand': device_brand,
        'device_ram': device_ram,
        'device_storage': device_storage,
        'sap_prediction': sap_predictions.tolist(),  # Convert predictions to a list before saving to MongoDB
        'sld_prediction': sld_predictions.tolist(),
        'created_at': datetime.utcnow()
    })

    return jsonify({'message': 'Prediction successful', 'SAP_Predictions': sap_predictions.tolist(), 'SLD_Predictions': sld_predictions.tolist()})


@predict.route('/price_model_bulk', methods=['POST'])
@jwt_required
def price_predict_bulk():
    file = request.files.get('file')
    
    if not file:
        return jsonify({'message': 'No file provided'}), 400
    
    try:
        # Read the CSV file
        df = pd.read_csv(file)
        # Strip invisible characters from column names
        df.columns = df.columns.str.strip('\u2060')
        print("Column Names:", df.columns.tolist())  # Print column names
    except Exception as e:
        return jsonify({'message': f'Error reading file: {str(e)}'}), 400

    # Ensure all required columns are present in the CSV
    required_columns = ['region', 'device_RAM', 'device_storage', 'new_device_price', 'device_category', 'condition_category', 'months_used']
    if not all(col in df.columns for col in required_columns):
        return jsonify({'message': f'Missing required columns. Required columns are: {required_columns}'}), 400

    # Get exchange rate
    url = 'https://v6.exchangerate-api.com/v6/f50628742f57bef260de9dba/latest/NGN'
    response = requests.get(url)
    if response.status_code != 200 or 'conversion_rates' not in response.json():
        return jsonify({'message': 'Failed to retrieve exchange rates'}), 500
    
    exchange_data = response.json()
    exchange_rate = exchange_data['conversion_rates']['USD']

    # Convert new_device_price from Naira to dollars and add new_device_price_dollars column
    df['new_price_dollars'] = convert_to_dollar(df['new_device_price'], exchange_rate)

    # Preprocess the data using the loaded preprocessing steps
    preprocessed_data = preprocessor.transform(df)
    
    # Make predictions
    predictions = model.predict(preprocessed_data)
    
    results = []
    documents = []

    access_token = request.headers.get('Authorization')
    decoded_token = jwt.decode(access_token, 'bd0467ad425dd8508a78619a393502584d9aa6b2', algorithms=['HS256'])
    user_id = decoded_token['user_id']
    user_email = decoded_token['email']
    
    user_data = mongo.db.users.find_one({'email': user_email})
    user_name = user_data['fullname']
    
    for idx, row in df.iterrows():
        predicted_trade_in_price = predictions[idx]
        result = mongo.db.devices.find_one({'category': row['device_category']})
        profit_percent = int(result['profit_percent']) / 100
        # Calculate the preowned value of the device
        preowned_value = (profit_percent * predicted_trade_in_price) + predicted_trade_in_price
        naira_price = convert_to_naira(predicted_trade_in_price, exchange_rate)
        preowned_naira = convert_to_naira(preowned_value, exchange_rate)
        
        result = {
            'region': row['region'],
            'device_RAM': row['device_RAM'],
            'device_storage': row['device_storage'],
            'new_device_price': row['new_device_price'],
            'device_category': row['device_category'],
            'condition_category': row['condition_category'],
            'months_used': row['months_used'],
            'predicted_trade_in_price': naira_price,
            'preowned_value': preowned_naira,
        }
        
        results.append(result)
        
        document = {
            'user_id': user_id,
            'user_name': user_name,
            'region': row['region'],
            'device_RAM': row['device_RAM'],
            'device_storage': row['device_storage'],
            'new_device_price': naira_price,
            'device_category': row['device_category'],
            'condition_category': row['condition_category'],
            'months_used': row['months_used'],
            'predicted_trade_in_price': naira_price,
            'preowned_value': preowned_naira,
            'created_at': datetime.utcnow()
        }
        documents.append(document)
    
    if documents:
        mongo.db.trades.insert_many(documents)
    
    # return jsonify({'message': 'Predictions successful', 'predictions': results})
    # Convert results to a DataFrame
    results_df = pd.DataFrame(results)
    
    # Create a CSV file from the DataFrame
    csv_buffer = io.StringIO()
    results_df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    return send_file(
        io.BytesIO(csv_buffer.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='predictions.csv'
    )

@predict.route('/insurance_model_bulk', methods=['POST'])
def insurance_predict_bulk():
    file = request.files.get('file')
    
    if not file:
        return jsonify({'message': 'No file provided'}), 400
    
    try:
        # Read the CSV file
        df = pd.read_csv(file)
    except Exception as e:
        return jsonify({'message': f'Error reading file: {str(e)}'}), 400
    
    # Ensure all required columns are present in the CSV
    required_columns = ['device_price', 'device_brand', 'device_ram', 'device_storage', 'screen_price']
    if not all(col in df.columns for col in required_columns):
        return jsonify({'message': f'Missing required columns. Required columns are: {required_columns}'}), 400
    
    # Separate data for SAP and SLD based on the presence of screen_price
    sap_data = df[['device_price', 'device_brand', 'device_ram', 'device_storage']]
    sld_data = df[['device_price', 'device_brand', 'device_ram', 'device_storage', 'screen_price']]
    
    # Preprocess the data using the loaded preprocessing steps
    sap_preprocessed_data = sap_preprocessor.transform(sap_data)
    sld_preprocessed_data = sld_preprocessor.transform(sld_data)
    
    # Make predictions
    sap_predictions = sap_model.predict(sap_preprocessed_data)
    sld_predictions = sld_model.predict(sld_preprocessed_data)
    
    results = []
    documents = []
    
    for idx, row in df.iterrows():
        sap_prediction = sap_predictions[idx] if not pd.isna(row['screen_price']) else None
        sld_prediction = sld_predictions[idx] if pd.notna(row['screen_price']) else None
        
        result = {
            'device_price': row['device_price'],
            'device_brand': row['device_brand'],
            'device_ram': row['device_ram'],
            'device_storage': row['device_storage'],
            'screen_price': row['screen_price'],
            'sap_prediction': sap_prediction,
            'sld_prediction': sld_prediction
        }
        
        results.append(result)
        
        document = {
            'device_price': row['device_price'],
            'device_brand': row['device_brand'],
            'device_ram': row['device_ram'],
            'device_storage': row['device_storage'],
            'screen_price': row['screen_price'],
            'sap_prediction': sap_prediction,
            'sld_prediction': sld_prediction,
            'created_at': datetime.utcnow()
        }
        documents.append(document)
    
    if documents:
        mongo.db.insurances.insert_many(documents)
    
    # return jsonify({'message': 'Predictions successful', 'predictions': results})
    results_df = pd.DataFrame(results)
    
    # Create a CSV file from the DataFrame
    csv_buffer = io.StringIO()
    results_df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    return send_file(
        io.BytesIO(csv_buffer.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name='predictions.csv'
    )

    