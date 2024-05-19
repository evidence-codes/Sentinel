from flask import Flask
from config import Config
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

mongo = PyMongo()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
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
    

    from .routes import main
    app.register_blueprint(main)
    
    # print("Registering auth blueprint...")
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/admin')
    
    from .predictions import predict as predict_blueprint
    app.register_blueprint(predict_blueprint, url_prefix='/predict')
    
    from .device import device as device_blueprint
    app.register_blueprint(device_blueprint, url_prefix='/device')
    # print("Auth blueprint registered.")
    
    # for rule in app.url_map.iter_rules():
    #     print(rule)

    return app