from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.fullname = user_data['fullname']
        self.username = user_data['username']
        self.email = user_data['email']
        self.password = user_data['password']