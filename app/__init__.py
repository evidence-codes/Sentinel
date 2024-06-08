from flask import Flask
from flask_cors import CORS
from config import Config
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from .routes import main as main_blueprint
from bson import ObjectId
from .models.user_model import User

mongo = PyMongo()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, static_folder='static/assets', template_folder='static')
    CORS(app)
    app.config.from_object(Config)
    
    
    mongo.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    
    # Log connection status
    with app.app_context():
        try:
            mongo.db.command('ping')
            app.logger.info("Successfully connected to MongoDB")
        except Exception as e:
            app.logger.error(f"Error connecting to MongoDB: {e}")  
            
     
    @login_manager.user_loader
    def load_user(user_id):
        user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if not user_data:
            return None
        return User(user_data)           
    

    app.register_blueprint(main_blueprint)
    
    # print("Registering auth blueprint...")
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
    
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/api/admin')
    
    from .predictions import predict as predict_blueprint
    app.register_blueprint(predict_blueprint, url_prefix='/api/predict')
    
    from .device import device as device_blueprint
    app.register_blueprint(device_blueprint, url_prefix='/api/device')
    
    from .data import train as train_blueprint
    app.register_blueprint(train_blueprint, url_prefix='/api/data')
    
    from .user import user as user_blueprint
    app.register_blueprint(user_blueprint,url_prefix='/api/user')
    # print("Auth blueprint registered.")
    
    # for rule in app.url_map.iter_rules():
    #     print(rule)

    return app
