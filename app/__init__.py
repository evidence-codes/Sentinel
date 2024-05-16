from flask import Flask
from flask_pymongo import PyMongo
from config import Config

mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    mongo.init_app(app)
    
    # Log connection status
    with app.app_context():
        try:
            mongo.db.command('ping')
            app.logger.info("Successfully connected to MongoDB")
        except Exception as e:
            app.logger.error(f"Error connecting to MongoDB: {e}")

    from .routes import main
    app.register_blueprint(main)

    return app
