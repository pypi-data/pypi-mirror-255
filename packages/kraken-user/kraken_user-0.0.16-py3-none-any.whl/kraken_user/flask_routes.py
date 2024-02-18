


from flask import Flask
from flask import request
from flask import Response
from flask import redirect
from flask import url_for
from flask import jsonify
from kraken_user.helpers import json

from kraken_user import kraken_user as m
from kraken_user.class_kraken_user import User
from kraken_user.class_kraken_users import Users

UPLOAD_FOLDER = '/path/to/the/uploads'

# Initialize flask app
app = Flask(__name__,
            static_url_path='',
            static_folder='static',
            template_folder='templates')
app.secret_key = b'_5#mn"F4Q8znxec]/'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['GET', 'POST'])
def main_get():

    key = 'name'
    value = request.args.get(key)

    if value:
        r = User()
        records = r.autocomplete(key, '%' + str(value) + '%')
        return jsonify(records)


    content = "Api for kraken_user"
    return Response(content)


@app.route('/<key>/<value>', methods=['GET', 'POST'])
def search_path_get(key, value):

    r = User()
    records = r.search(key, '%' + value + '%')
    return jsonify(records)


@app.route('/autocomplete', methods=['GET', 'POST'])
def autocomplete_params_get():

    key = 'name'
    value = request.args.get(key)

    r = User()
    records = r.autocomplete(key, '%' + str(value) + '%')
    return jsonify(records)



@app.route('/autocomplete/<key>/<value>', methods=['GET', 'POST'])
def autocomplete_path_get(key, value):

    r = User()
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



def run_api():
    app.run(host='0.0.0.0', debug=False)


    