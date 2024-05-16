from flask import Blueprint

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return "Hello, Flask!"

@main.route('/login')
def login():
    return "Login here"