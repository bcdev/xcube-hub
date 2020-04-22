# The MIT License (MIT)
# Copyright (c) 2020 by the xcube development team and contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import uuid

import flask
import flask_cors
from flask import jsonify
import xcube_gen.api as api
from xcube_gen.auth0 import AuthError, requires_auth
from xcube_gen.cfg import Cfg
from xcube_gen.controllers import datastores, jobs
from xcube_gen.controllers import users, user_namespaces


def new_app():
    """Create the service app."""
    app = flask.Flask('xcube-genserv')
    Cfg.load_config_once()

    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        return response

    flask_cors.CORS(app)

    @app.route('/jobs/<user_name>', methods=['GET', 'POST', 'DELETE'])
    @requires_auth
    def _jobs(user_name: str):
        if flask.request.method == 'GET':
            return jobs.list(user_name=user_name)
        if flask.request.method == 'POST':
            job_id = f"xcube-gen-{str(uuid.uuid4())}"
            return jobs.create(user_name=user_name, job_id=job_id, sh_cmd='gen', cfg=flask.request.json)
        if flask.request.method == 'DELETE':
            return jobs.delete_all(user_name=user_name)

    @app.route('/jobs/<user_name>/<job_id>', methods=['GET', 'DELETE'])
    @requires_auth
    def _job(user_name: str, job_id: str):
        if flask.request.method == "GET":
            return jobs.get(user_name=user_name, job_id=job_id)
        if flask.request.method == "DELETE":
            return jobs.delete_one(user_name=user_name, job_id=job_id)

    @app.route('/jobs/<user_name>/<job_id>/status', methods=['GET'])
    @requires_auth
    def _job_status(user_name: str, job_id: str):
        return jobs.status(user_name=user_name, job_id=job_id)

    @app.route('/jobs/<user_name>/<job_id>/result', methods=['GET'])
    @requires_auth
    def _result(user_name: str, job_id: str):
        return jobs.result(user_name=user_name, job_id=job_id)

    @app.route('/user_namespaces/<user_name>', methods=['GET', 'POST', 'DELETE'])
    @requires_auth
    def _user_namespace(user_name: str):
        if flask.request.method == 'GET':
            return user_namespaces.list()
        elif flask.request.method == 'POST':
            return user_namespaces.create(user_name=user_name)
        elif flask.request.method == 'DELETE':
            return user_namespaces.delete(user_name=user_name)

    @app.route('/user_namespaces', methods=['GET'])
    @requires_auth
    def _user_namespaces():
        return user_namespaces.list()

    @app.route('/datastores', methods=['GET'])
    @requires_auth
    def _datastores():
        return api.ApiResponse.success(result=datastores.get_datastores())

    @app.route('/users/<user_name>/data', methods=['GET', 'PUT', 'DELETE'])
    def _user_data(user_name: str):
        if flask.request.method == 'GET':
            users.get_user_data(user_name)
        elif flask.request.method == 'PUT':
            users.put_user_data(user_name, flask.request.json)
        elif flask.request.method == 'DELETE':
            users.delete_user_data(user_name)
        return api.ApiResponse.success()

    @app.route('/users/<user_name>/punits', methods=['PUT', 'DELETE'])
    def _update_processing_units(user_name: str):
        try:
            if flask.request.method == 'PUT':
                users.update_processing_units(user_name, flask.request.json, factor=1)
            elif flask.request.method == 'DELETE':
                users.update_processing_units(user_name, flask.request.json, factor=-1)
        except api.ApiError as e:
            return e.response
        return api.ApiResponse.success()

    @app.route('/docs/<name>', methods=['GET'])
    def _docs(name: str):
        return api.main()

    @app.route('/', methods=['GET'])
    def _main():
        return api.main()

    return app


def start(host: str = None,
          port: int = None,
          debug: bool = False):
    """
    Start the service.

    :param host: The hostname to listen on. Set this to ``'0.0.0.0'`` to
        have the server available externally as well. Defaults to ``'127.0.0.1'``.
    :param port: The port to listen on. Defaults to ``5000``.
    :param debug: If given, enable or disable debug mode.
    """
    new_app().run(host=host, port=port, debug=debug)
