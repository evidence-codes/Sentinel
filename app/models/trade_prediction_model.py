from flask_login import UserMixin

class Trade(UserMixin):
    def __init__(self, trade_data):
        self.id = str(trade_data['_id'])
        self.manufacturer = trade_data['manufacturer']
        self.storage = trade_data['storage']
        self.storage = trade_data['price']
        self.prediction = trade_data['prediction']