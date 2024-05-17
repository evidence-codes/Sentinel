#this is our main entry
export FLASK_APP=run.py

#you can remove this in deployment server
#it's useful so we can see any change from our code directly when developing
export FLASK_DEBUG=1

#running the app
flask run













# Log connection status
    # with app.app_context():
    #     try:
    #         mongo.db.command('ping')
    #         app.logger.info("Successfully connected to MongoDB")
    #     except Exception as e:
    #         app.logger.error(f"Error connecting to MongoDB: {e}")