from flask import Blueprint, send_from_directory, render_template
import os

main = Blueprint('main', __name__, static_folder='static/assets', template_folder='static')

# @main.route('/')
# def home():
#     # return send_from_directory(os.path.join(main.root_path, 'static'), 'index.html')
#     return "Welcome to the Flask app!"

# @main.route('/about')
# def about():
#     return "This is the about page."

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/<path:path>')
def static_proxy(path):
    if os.path.exists(os.path.join(main.template_folder, path)):
        return send_from_directory(main.template_folder, path)
    else:
        return send_from_directory(main.template_folder, 'index.html')
