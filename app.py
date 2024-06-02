# from waitress import serve
from app import create_app
from flask_cors import CORS

app = create_app()

#cors_origins = ["http://localhost:5173"]

#CORS(app, resources={r"/*": {"origins": cors_origins}}, supports_credentials=True)

CORS(app)

@app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

if __name__ == '__main__':
    # serve(app, host="0.0.0.0", port=8000)
    app.run()
