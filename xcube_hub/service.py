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
import hashlib
import os
from typing import Optional

import flask
import flask_cors
import werkzeug
from flask_cors import cross_origin
from flask_oidc import OpenIDConnect
from flask import g
from werkzeug import exceptions

import xcube_hub.api as api
from xcube_hub import auth0
from xcube_hub.auth0 import Auth0, API_AUTH_IDENTIFIER
from xcube_hub.cfg import Cfg
from xcube_hub.controllers import datastores, callback, cate, auth
from xcube_hub.controllers import info
from xcube_hub.controllers import jobs
from xcube_hub.controllers import sizeandcost
from xcube_hub.controllers import users
from xcube_hub.controllers import viewer
from dotenv import load_dotenv
from xcube_hub.keyvaluedatabase import KeyValueDatabase


# noinspection PyStatementEffect
def raise_for_invalid_json():
    try:
        flask.request.json
    except exceptions.HTTPException as e:
        raise api.ApiError(400, "Invalid JSON in request body " + str(e))


def new_app(prefix: str = "", cache_provider: str = "leveldb", static_url_path='', static_folder='', dotenv_path: str = '.env'):
    """Create the service app."""
    load_dotenv()
    app = flask.Flask('xcube-genserv', static_url_path, static_folder=static_folder)
    flask_cors.CORS(app)
    Cfg.load_config_once()
    KeyValueDatabase.instance(provider=cache_provider)

    @app.route(prefix + '/', methods=['GET'])
    def _service_info():
        return api.ApiResponse.success(info.service_info())

    try:
        launch_cate = int(os.environ.get("LAUNCH_CATE", 0))
    except ValueError:
        raise api.ApiError(500, "Error: LAUNCH_CATE must be 0 or 1.")

    try:
        launch_xcube_gen = int(os.environ.get("LAUNCH_XCUBE_GEN", 0))
    except ValueError:
        raise api.ApiError(500, "Error: LAUNCH_XCUBE_GEN must be 0 or 1.")

    try:
        launch_xcube_geodb = int(os.environ.get("LAUNCH_XCUBE_GEODB", 0))
    except ValueError:
        raise api.ApiError(500, "Error: LAUNCH_XCUBE_GEODB must be 0 or 1.")

    if launch_cate == 1:
        app = new_cate_app(app, prefix)
    if launch_xcube_gen == 1:
        app = new_xcube_gen_app(app, prefix)
    if launch_xcube_geodb == 1:
        app = new_xcube_geodb_app(app, prefix)

    # Flask Error Handler
    @app.errorhandler(werkzeug.exceptions.HTTPException)
    def handle_http_exception(e):
        return api.ApiResponse.error(e.description, e.code)

    if os.environ.get('XCUBE_GEN_MOCK_SERVICES') == '1':
        from .servicemocks import extend_app
        extend_app(app, prefix)

    return app


def new_cate_app(app, prefix: str = ""):

    oidc_client_secrets_file = os.environ.get('OIDC_CLIENT_SECRETS_FILE', False)
    if not oidc_client_secrets_file:
        raise api.ApiError(500, "ERROR: No oidc clients secret file.")

    app.config.update({
        'SECRET_KEY': 'SomethingNotEntirelySecret',
        'TESTING': True,
        'DEBUG': True,
        'OIDC_CLIENT_SECRETS': oidc_client_secrets_file,
        'OIDC_ID_TOKEN_COOKIE_SECURE': False,
        'OIDC_REQUIRE_VERIFIED_EMAIL': False,
        # 'OVERWRITE_REDIRECT_URI': 'http://localhost:3000/login',
        'OIDC_USER_INFO_ENABLED': True,
        'OIDC_OPENID_REALM': 'https://xcube-gen.brockmann-consult.de/api/v1/',
        'OIDC_SCOPES': ['openid', 'email', 'profile'],
        'OIDC_INTROSPECTION_AUTH_METHOD': 'bearer'
    })

    oidc = OpenIDConnect(app)

    @app.route(prefix + '/user/<user_id>/webapi', methods=['GET', 'POST', 'DELETE'])
    @cross_origin(supports_credentials=True, allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'])
    @oidc.accept_token(require_token=True)
    def _cate_webapi(user_id: str):
        try:
            # _accept_role('user')
            if flask.request.method == "GET":
                return api.ApiResponse.success(cate.get_status(user_id=user_id))
            if flask.request.method == "POST":
                return api.ApiResponse.success(cate.launch_cate(user_id=user_id))
            if flask.request.method == "DELETE":
                return api.ApiResponse.success(cate.delete_cate(user_id=user_id, prune=True))
        except api.ApiError as e:
            return e.response

    @app.route(prefix + '/user/<user_id>/webapi/shutdown', methods=['DELETE'])
    @cross_origin(supports_credentials=True, allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'])
    def _cate_delete_webapi(user_id: str):
        try:
            # _accept_role('user')
            prefer_header = flask.request.headers.get('Prefer', False)
            prune = (prefer_header and prefer_header == 'prune') or False

            if flask.request.method == "DELETE":
                return api.ApiResponse.success(cate.delete_cate(user_id=user_id, prune=prune))
        except api.ApiError as e:
            return e.response

    @app.route(prefix + '/webapi/count', methods=['GET'])
    @cross_origin(supports_credentials=True, allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'])
    def _cate_count_webapis():
        try:
            if flask.request.method == "GET":
                return api.ApiResponse.success(cate.get_pod_count(label_selector="purpose=cate-webapi"))
        except api.ApiError as e:
            return e.response

    @app.route(prefix + '/webapi/available', methods=['GET'])
    @cross_origin(supports_credentials=True, allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'])
    def _cate_get_webapi_availabale():
        try:
            if flask.request.method == "GET":
                pod_count = cate.get_pod_count(label_selector="purpose=cate-webapi")
                if pod_count < 20:
                    return api.ApiResponse.success({'service_available': True})
                else:
                    raise api.ApiError(428, "No further service available")
        except api.ApiError as e:
            return e.response

    return app


def new_xcube_gen_app(app, prefix: str = ""):

    @app.route(prefix + '/jobs/<user_id>', methods=['GET', 'PUT', 'DELETE'])
    @auth0.requires_auth0()
    def _jobs(user_id: str):
        try:
            Auth0.raise_for_invalid_user_id(user_id=user_id)
            raise_for_invalid_json()
            if flask.request.method == 'GET':
                return jobs.list(user_id=user_id)
            if flask.request.method == 'PUT':
                return jobs.create(user_id=user_id, cfg=flask.request.json)
            if flask.request.method == 'DELETE':
                return jobs.delete_all(user_id=user_id)
        except api.ApiError as e:
            return e.response

    @app.route(prefix + '/jobs/<user_id>/<job_id>', methods=['GET', 'DELETE'])
    @auth0.requires_auth0()
    def _job(user_id: str, job_id: str):
        try:
            Auth0.raise_for_invalid_user_id(user_id)
            if flask.request.method == "GET":
                return jobs.get(user_id=user_id, job_id=job_id)
            if flask.request.method == "DELETE":
                return jobs.delete_one(user_id=user_id, job_id=job_id)
        except api.ApiError as e:
            return e.response

    def _accept_role(role: str):
        token_info = g.oidc_token_info
        if role not in token_info['resource_access']['cate-login']['roles']:
            raise api.ApiError(403,
                               f"Access denied. You need {role} access to cate. \n If registered already, "
                               f"your account might be in the process of being approved.")

    @app.route(prefix + '/cubes/<user_id>/xcviewer', methods=['GET', 'POST'])
    @auth0.requires_auth0()
    def _cubes_viewer(user_id: str):
        try:
            Auth0.raise_for_invalid_user_id(user_id)
            if flask.request.method == "GET":
                return api.ApiResponse.success(viewer.get_status(user_id=user_id))
            if flask.request.method == "POST":
                return api.ApiResponse.success(viewer.launch_viewer(user_id, flask.request.json))
        except api.ApiError as e:
            return e.response

    @app.route(prefix + '/datastores', methods=['GET'])
    def _datastores():
        return api.ApiResponse.success(result=datastores.get_datastores())

    @app.route(prefix + '/sizeandcost', methods=['POST'])
    def _size_and_cost():
        try:
            raise_for_invalid_json()
            return api.ApiResponse.success(result=sizeandcost.get_size_and_cost(flask.request.json))
        except api.ApiError as e:
            return e.response

    # noinspection InsecureHash
    @app.route(prefix + '/users/<user_name>/data', methods=['GET', 'PUT', 'DELETE'])
    @auth0.requires_auth0()
    def _user_data(user_name: str):
        try:
            res = hashlib.md5(user_name.encode())
            user_id = 'a' + res.hexdigest()
            Auth0.raise_for_invalid_user_id(user_id)
            raise_for_invalid_json()

            if flask.request.method == 'GET':
                user_data = users.get_user_data(user_name)
                return api.ApiResponse.success(result=user_data)
            elif flask.request.method == 'PUT':
                users.put_user_data(user_name, flask.request.json)
                return api.ApiResponse.success()
            elif flask.request.method == 'DELETE':
                users.delete_user_data(user_name)
                return api.ApiResponse.success()
        except api.ApiError as e:
            return e.response

    # noinspection InsecureHash
    @app.route(prefix + '/users/<user_name>/punits', methods=['GET', 'PUT', 'DELETE'])
    @auth0.requires_auth0()
    def _processing_units(user_name: str):
        try:
            raise_for_invalid_json()
            res = hashlib.md5(user_name.encode())
            user_id = 'a' + res.hexdigest()
            Auth0.raise_for_invalid_user_id(user_id)

            if flask.request.method == 'GET':
                Auth0.requires_permissions(['read:punits'])
                include_history = flask.request.args.get('history', False)
                processing_units = users.get_processing_units(user_name, include_history=include_history)
                return api.ApiResponse.success(result=processing_units)
            elif flask.request.method == 'PUT':
                Auth0.requires_permissions(['put:punits'])
                users.add_processing_units(user_name, flask.request.json)
                return api.ApiResponse.success()
            elif flask.request.method == 'DELETE':
                Auth0.requires_permissions(['put:punits'])
                users.subtract_processing_units(user_name, flask.request.json)
                return api.ApiResponse.success()
        except api.ApiError as e:
            return e.response

    @app.route(prefix + '/jobs/<user_id>/<job_id>/callback', methods=['GET', 'PUT', 'DELETE'])
    @auth0.requires_auth0()
    def _callback(user_id: str, job_id: str):
        try:
            Auth0.raise_for_invalid_user_id(user_id=user_id)
            if flask.request.method == 'GET':
                Auth0.requires_permissions(['read:callback', 'submit:job'])
                res = callback.get_callback(user_id, job_id)
                return api.ApiResponse.success(result=res)
            elif flask.request.method == 'PUT':
                raise_for_invalid_json()
                Auth0.requires_permissions(['put:callback', 'submit:job'])
                callback.put_callback(user_id, job_id, flask.request.json)
                return api.ApiResponse.success()
            elif flask.request.method == "DELETE":
                Auth0.requires_permissions(['delete:callback'])
                callback.delete_callback(user_id, job_id)
                return api.ApiResponse.success()
        except api.ApiError as e:
            return e.response

    @app.route(prefix + '/viewer')
    def _viewer():
        return app.send_static_file('viewer/index.html')

    return app


def new_xcube_geodb_app(app, prefix: str = ""):
    @app.route(prefix + '/geodb/credentials', methods=['GET'])
    def _auth_app_credentials():
        try:
            res = auth.auth_login_app()
            return api.ApiResponse.success(result=res)
        except api.ApiError as e:
            return e.response

    @app.route(prefix + '/auth/user', methods=['POST', 'GET', 'DELETE'], defaults={'user_id': None})
    @app.route(prefix + '/auth/user/<user_id>')
    @auth0.requires_auth0(audience=API_AUTH_IDENTIFIER)
    def user(user_id: Optional[str] = None):
        try:
            payload = flask.request.json
            token = Auth0.get_token_auth_header()
            if flask.request.method == 'POST':
                auth.register_user(token=token, payload=payload)
                res = "success"
            elif flask.request.method == 'GET':
                res = auth.get_user(token=token, user_id=user_id)
            elif flask.request.method == 'DELETE':
                auth.delete_user(token=token, user_id=user_id)
                res = "success"
            else:
                res = "failed"
            return api.ApiResponse.success(result=res)
        except api.ApiError as e:
            return e.response
        except BaseException as e:
            return api.ApiResponse.error(e)

    @app.route(prefix + '/auth/role', methods=['PUT'])
    @auth0.requires_auth0(audience=API_AUTH_IDENTIFIER)
    def role(user_id: str, role_id: str):
        try:
            payload = flask.request.json
            token = Auth0.get_token_auth_header()
            auth.add_user_to_role(token=token, user_id=user_id, role_id=role_id)
            return api.ApiResponse.success(result="success")
        except api.ApiError as e:
            return e.response

    return app


def start(host: str = None,
          port: int = None,
          debug: bool = False,
          cache_provider: str = "leveldb"):
    """
    Start the service.

    :param cache_provider:
    :param host: The hostname to listen on. Set this to ``'0.0.0.0'`` to
        have the server available externally as well. Defaults to ``'127.0.0.1'``.
    :param port: The port to listen on. Defaults to ``5000``.
    :param debug: If given, enable or disable debug mode.
    """
    new_app(cache_provider=cache_provider).run(host=host, port=port, debug=debug)
