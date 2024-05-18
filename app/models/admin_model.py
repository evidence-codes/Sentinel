from flask_login import UserMixin

class Admin(UserMixin):
    def __init__(self, admin_data):
        self.id = str(admin_data['_id'])
        self.username = admin_data['username']
        self.email = admin_data['email']
        self.password = admin_data['password']