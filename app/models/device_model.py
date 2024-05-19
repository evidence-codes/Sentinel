from flask_login import UserMixin

class Device(UserMixin):
    def __init__(self, device_data):
        self.id = str(device_data['_id'])
        self.name = device_data['name']
        self.category = device_data['category']
        self.profit_percent = device_data['profit_percent']