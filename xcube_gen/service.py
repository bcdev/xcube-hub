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
import werkzeug
from flask import jsonify
import xcube_gen.api as api
from xcube_gen.auth import AuthError, requires_auth
from xcube_gen.cfg import Cfg
from xcube_gen.controllers import jobs
from xcube_gen.controllers import user_namespaces
from xcube_gen.controllers import datastores
from xcube_gen.controllers import sizeandcost
from xcube_gen.controllers import users


def new_app(prefix: str = ""):
    """Create the service app."""
    app = flask.Flask('xcube-genserv')
    Cfg.load_config_once()

    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        return response

    flask_cors.CORS(app)

    @app.route(prefix + '/jobs/<user_name>', methods=['GET', 'POST', 'DELETE'])
    @requires_auth
    def _jobs(user_name: str):
        try:
            if flask.request.method == 'GET':
                return jobs.list(user_name=user_name)
            if flask.request.method == 'POST':
                job_id = f"xcube-gen-{str(uuid.uuid4())}"
                return jobs.create(user_name=user_name, job_id=job_id, sh_cmd='gen', cfg=flask.request.json)
            if flask.request.method == 'DELETE':
                return jobs.delete_all(user_name=user_name)
        except api.ApiError as e:
            return e.response

    @app.route(prefix + '/jobs/<user_name>/<job_id>', methods=['GET', 'DELETE'])
    @requires_auth
    def _job(user_name: str, job_id: str):
        try:
            if flask.request.method == "GET":
                return jobs.get(user_name=user_name, job_id=job_id)
            if flask.request.method == "DELETE":
                return jobs.delete_one(user_name=user_name, job_id=job_id)
        except api.ApiError as e:
            return e.response

    @app.route(prefix + '/jobs/<user_name>/<job_id>/status', methods=['GET'])
    @requires_auth
    def _job_status(user_name: str, job_id: str):
        try:
            return jobs.status(user_name=user_name, job_id=job_id)
        except api.ApiError as e:
            return e.response

    @app.route(prefix + '/jobs/<user_name>/<job_id>/result', methods=['GET'])
    @requires_auth
    def _result(user_name: str, job_id: str):
        try:
            return jobs.result(user_name=user_name, job_id=job_id)
        except api.ApiError as e:
            return e.response

    @app.route(prefix + '/user_namespaces/<user_name>', methods=['GET', 'POST', 'DELETE'])
    @requires_auth
    def _user_namespace(user_name: str):
        try:
            if flask.request.method == 'GET':
                return user_namespaces.list()
            elif flask.request.method == 'POST':
                return user_namespaces.create(user_name=user_name)
            elif flask.request.method == 'DELETE':
                return user_namespaces.delete(user_name=user_name)
        except api.ApiError as e:
            return e.response

    @app.route(prefix + '/user_namespaces', methods=['GET'])
    @requires_auth
    def _user_namespaces():
        try:
            return user_namespaces.list()
        except api.ApiError as e:
            return e.response

    @app.route(prefix + '/datastores', methods=['GET'])
    def _datastores():
        return api.ApiResponse.success(result=datastores.get_datastores())

    @app.route(prefix + '/sizeandcost', methods=['POST'])
    def _size_and_cost():
        return api.ApiResponse.success(result=sizeandcost.get_size_and_cost(flask.request.json))

    @app.route(prefix + '/users/<user_id>/data', methods=['GET', 'PUT', 'DELETE'])
    @requires_auth
    def _user_data(user_id: str):
        try:
            if flask.request.method == 'GET':
                user_data = users.get_user_data(user_id)
                return api.ApiResponse.success(result=user_data)
            elif flask.request.method == 'PUT':
                users.put_user_data(user_id, flask.request.json)
                return api.ApiResponse.success()
            elif flask.request.method == 'DELETE':
                users.delete_user_data(user_id)
                return api.ApiResponse.success()
        except api.ApiError as e:
            return e.response

    @app.route(prefix + '/users/<user_id>/punits', methods=['GET', 'PUT', 'DELETE'])
    @requires_auth
    def _update_processing_units(user_id: str):
        try:
            if flask.request.method == 'GET':
                include_history = flask.request.args.get('history', False)
                processing_units = users.get_processing_units(user_id, include_history=include_history)
                return api.ApiResponse.success(result=processing_units)
            elif flask.request.method == 'PUT':
                users.add_processing_units(user_id, flask.request.json)
                return api.ApiResponse.success()
            elif flask.request.method == 'DELETE':
                users.subtract_processing_units(user_id, flask.request.json)
                return api.ApiResponse.success()
        except api.ApiError as e:
            return e.response

    @app.route('/', methods=['GET'])
    def _main_assure_health_test():
        return api.main()

    @app.route(prefix + '/', methods=['GET'])
    def _main():
        return api.main()

    # Flask Error Handler
    @app.errorhandler(werkzeug.exceptions.HTTPException)
    def handle_http_exception(e):
        return api.ApiResponse.error(e.description, e.code)

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
