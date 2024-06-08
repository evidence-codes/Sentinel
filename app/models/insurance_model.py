from flask_login import UserMixin

class Insurance(UserMixin):
    def __init__(self, insurance_data):
        self.id = str(insurance_data['_id'])
        self.device_price = insurance_data['device_price']
        self.device_brand = insurance_data['device_brand']
        self.device_ram = insurance_data['device_ram']
        self.device_storage = insurance_data['device_storage']
        self.screen_price = insurance_data['screen_price']
        self.sap_prediction = insurance_data['sap_prediction']
        self.sld_prediction = insurance_data['sld_prediction']
        self.created_at = insurance_data['created_at']