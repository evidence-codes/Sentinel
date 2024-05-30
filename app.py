# from waitress import serve
from app import create_app
from flask_cors import CORS

app = create_app()
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

if __name__ == '__main__':
    # serve(app, host="0.0.0.0", port=8000)
    app.run()