from flask import Blueprint, send_from_directory, render_template
import os

main = Blueprint('main', __name__)

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
    file_name = path.split('/')[-1]
    dir_name = os.path.join(main.static_folder, '/'.join(path.split('/')[:-1]))
    return send_from_directory(dir_name, file_name)
