from flask_login import UserMixin

class Trade(UserMixin):
    def __init__(self, trade_data):
        self.id = str(trade_data['_id'])
        self.user_id = trade_data['user_id']
        self.user_name = trade_data['user_name']
        self.region = trade_data['region']
        self.device_RAM = trade_data['device_RAM']
        self.device_storage = trade_data['device_storage']
        self.new_price_dollars = trade_data['new_price_dollars']
        self.condition_category = trade_data['condition_category']
        self.months_used = trade_data['months_used']
        self.predicted_trade_in_price = trade_data['predicted_trade_in_price']
        self.preowned_value = trade_data['preowned_value']
        self.created_at = trade_data['created_at']
   