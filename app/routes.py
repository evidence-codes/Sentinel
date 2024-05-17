from flask import Blueprint

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return "Welcome to the Flask app!"

@main.route('/about')
def about():
    return "This is the about page."