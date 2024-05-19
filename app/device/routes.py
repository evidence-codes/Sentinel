from . import device
from flask import request, jsonify
from app.models import Device
from .. import mongo



@device.route('/add', methods=['POST'])
def add_device():
    data = request.json()
    name = data.get('name')
    category = data.get('category')
    profit_percent = data.get('profit_percent')
    
    if mongo.db.devices.find_one({'category': category}):
        return jsonify({'message': 'Device already registered'}), 400
    
    mongo.db.devices.insert_one({
        'name': name,
        'category': category,
        'profit_percent': profit_percent
    })
    
    return jsonify({'message': 'Device registered successfully'}), 201