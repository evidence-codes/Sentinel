# from waitress import serve
from app import create_app
from flask_cors import CORS

app = create_app()

#cors_origins = ["http://localhost:5173"]

#CORS(app, resources={r"/*": {"origins": cors_origins}}, supports_credentials=True)

CORS(app)


if __name__ == '__main__':
    # serve(app, host="0.0.0.0", port=8000)
    app.run()
