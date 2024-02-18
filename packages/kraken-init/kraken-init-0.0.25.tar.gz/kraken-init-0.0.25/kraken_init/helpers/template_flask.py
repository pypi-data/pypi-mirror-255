

def get_filename(name, directory=None):

    return f'{name}/flask_routes.py'


def get_content(name=None, directory=None):
    """
    """

    
    class_name = name.replace('kraken_', '')

    class_name = class_name.capitalize()
    class_name_collection = class_name + 's'
    
    dir = ''
    dir = directory.replace('/', '.') + '.' if directory else dir
    
    content = f'''


from flask import Flask
from flask import request
from flask import Response
from flask import redirect
from flask import url_for
from flask import jsonify
from flask import render_template
from flask import flash

import flask_login

from kraken_user import User

from {dir}{name}.helpers import json

from {dir}{name} import {name} as m
from {dir}{name}.class_{name} import {class_name}
from {dir}{name}.class_{name}s import {class_name_collection}

UPLOAD_FOLDER = '/path/to/the/uploads'

# Initialize flask app
app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')
app.secret_key = b'_5#mn"F4Q8znxec]/'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def main_get():

    key = 'name'
    value = request.args.get(key)

    if value:
        r = {class_name}()
        records = r.autocomplete(key, '%' + str(value) + '%')
        return jsonify(records)


    content = "Api for {name}"
    return Response(content)


@app.route('/protected', methods=['GET', 'POST'])
@flask_login.login_required
def test_get():

    user=flask_login.current_user
    return Response(render_template('main.html', data=data))


@app.route('/<key>/<value>', methods=['GET', 'POST'])
def search_path_get(key, value):

    r = {class_name}()
    records = r.search(key, '%' + value + '%')
    return jsonify(records)


@app.route('/autocomplete', methods=['GET', 'POST'])
def autocomplete_params_get():

    key = 'name'
    value = request.args.get(key)

    r = {class_name}()
    records = r.autocomplete(key, '%' + str(value) + '%')
    return jsonify(records)


@app.route('/autocomplete/<key>/<value>', methods=['GET', 'POST'])
def autocomplete_path_get(key, value):

    r = {class_name}()
    records = r.autocomplete(key, '%' + value + '%')
    return jsonify(records)


@app.route('/log', methods=['POST'])
def log_post(key, value):
    """Registers a log event
    """
    
    return Response('')

@app.route('/about', methods=['GET'])
def about_get(key, value):
    """Returns instrument record for api
    """

    record = m.get_instrument()
    return jsonify(record)



"""
User management routes
"""

@login_manager.user_loader
def user_loader(email):

    user = User()
    user.program = request.url_root
    user.membershipNumber = email
    user.api_get()
    return user

@login_manager.request_loader
def request_loader(request):

    user = User()
    user.program = request.url_root
    user.membershipNumber = request.form.get('email')
    user.api_get()
    return user


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        content = render_template('register.html', referrer=request.referrer)
        return Response(content)

    email = request.form['email']
    password = request.form['password']

    user = User()
    user.program = request.url_root
    user.membershipNumber = email
    user.add_credential(password)
    user.set_active()
    user.create()
    user.login()
    user.api_post()

    flask_login.login_user(user)

    return redirect('/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':

        content = render_template('login.html', referrer=request.referrer)

        return Response(content)

    email = request.form['email']
    password = request.form['password']
    referrer = request.form['referrer']

    if not referrer:
        referrer = '/'

    user = User()
    user.program = request.url_root
    user.set_membershipNumber(email)
    user.api_get()

    if user.authenticate(password):
        user.login()
        user.api_post()
        flask_login.login_user(user)
        flash('You were successfully logged in')
        return redirect(referrer)
    else:
        flash('Authorization failed')

    return 'Bad login'

@app.route('/logout')
def logout():
    user = flask_login.current_user
    user.logout()
    user.api_post()
    flask_login.logout_user()
    flash('You were successfully logged out')
    return redirect('/')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized', 401

"""
Main
"""
def run_api():
    app.run(host='0.0.0.0', debug=False)


    '''
    return content