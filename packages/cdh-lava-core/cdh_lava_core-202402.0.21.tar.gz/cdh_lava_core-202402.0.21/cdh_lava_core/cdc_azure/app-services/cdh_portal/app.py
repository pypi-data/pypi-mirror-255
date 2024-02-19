import json
import os
import datetime
import os

import jinja2
import requests
from flask import Flask, render_template, request, session, render_template_string

from approval_blueprint import approval_page
from datasets_blueprint import datasets_config_page
from great_expectations_blueprint import great_expectations_page
from shared_code import aad_helper, datalake_helper, session_helper, config_file_helper
from workflow_status_blueprint import workflow_status_page

app = Flask(__name__)
app.config['SECRET_KEY'] = '8c1877c2f2ae92291ba86113c669941f320041ae10776b79'

app.register_blueprint(approval_page)
app.register_blueprint(datasets_config_page)
app.register_blueprint(workflow_status_page)
app.register_blueprint(great_expectations_page)

environment = jinja2.Environment()
environment.filters['datetime'] = datetime


@app.route('/')
def home():  # put application's code here
    header = request.headers.get('X-MS-TOKEN-AAD-ACCESS-TOKEN')
    # return f"X-MS-TOKEN-AAD-ACCESS-TOKEN: {header}"
    session_helper.set_session_variables()
    return render_template('_layout.html')


@app.route('/test')
def test():  # put application's code here
    # token = aad_helper.get_aad_token(resource="https://graph.microsoft.com")
    # url = "https://graph.microsoft.com/v1.0/groups/29b8bb5b-934b-4f25-be08-3ff961fd98fb/members"
    # header = {"Authorization": f"Bearer {token}"}
    # response = requests.get(url, headers=header)
    # return response.json()
    datasets = config_file_helper.get_all_configured_dataasets()
    return json.dumps(datasets)


if __name__ == '__main__':
    app.run()
