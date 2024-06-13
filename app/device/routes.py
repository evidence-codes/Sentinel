from . import device
from flask import request, jsonify
from app.models import Device
from .. import mongo



@device.route('/edit-percent', methods=['POST'])
def add_device():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid input'}), 400
    
    category = data.get('category')
    profit_percent = data.get('profit_percent')
    
    if not category or not profit_percent:
        return jsonify({'error': 'Missing required fields'}), 400

    result = mongo.db.devices.find_one({'category': category})
    
    if result:
        mongo.db.devices.update_one(
            {'category': category},
            {'$set': {'profit_percent': profit_percent}}
        )
        return jsonify({'message': 'Device profit percent updated successfully'}), 200
    
    mongo.db.devices.insert_one({
        'category': category,
        'profit_percent': profit_percent
    })
    return jsonify({'message': 'Device registered successfully'}), 201