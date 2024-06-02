from flask import Blueprint, send_from_directory
import os

main = Blueprint('main', __name__)

@main.route('/')
def home():
    # return send_from_directory(os.path.join(main.root_path, 'static'), 'index.html')
    return "Welcome to the Flask app!"

@main.route('/about')
def about():
    return "This is the about page."
