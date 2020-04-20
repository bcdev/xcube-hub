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

import flask
import flask_cors

import xcube_gen.api as api
from xcube_gen.controllers import datastores
from xcube_gen.controllers import users


def new_app():
    """Create the service app."""
    app = flask.Flask('xcube-genserv')
    flask_cors.CORS(app)

    # '/jobs/<user_name>' [GET]  --> List
    # '/jobs/<user_name>' [POST]  --> Start job, returns Job ID
    # '/jobs/<user_name>/<job_id>' [DELETE]  --> Cancel/remove job
    # '/jobs/<user_name>/<job_id>/status' [GET]  --> Job status
    # '/jobs/<user_name>/<job_id>/result' [GET]  --> Job result

    @app.route('/process', methods=['POST'])
    def _job():
        return api.job(flask.request.json)

    @app.route('/delete', methods=['DELETE'])
    def _job_delete():
        return api.job_delete(flask.request.json)

    @app.route('/status/<job_name>', methods=['GET'])
    def _job_status(job_name):
        return api.job_status(job_name)

    @app.route('/result/<job_name>', methods=['GET'])
    def _result(job_name):
        return api.job_result(job_name)

    @app.route('/jobs', methods=['GET'])
    def _jobs():
        return api.jobs()

    @app.route('/purge', methods=['DELETE'])
    def _jobs_purge():
        return api.jobs_purge(flask.request.json)

    @app.route('/info', methods=['GET'])
    def _job_info():
        return api.job_info()

    @app.route('/datastores', methods=['GET'])
    def _datastores():
        return datastores.get_datastores()

    @app.route('/users/<user_name>/data', methods=['GET', 'PUT', 'DELETE'])
    def _user_data(user_name: str):
        if flask.request.method == 'GET':
            return users.get_user_data(user_name)
        elif flask.request.method == 'PUT':
            return users.put_user_data(user_name, flask.request.json)
        elif flask.request.method == 'DELETE':
            return users.delete_user_data(user_name)

    @app.route('/users/<user_name>/units/<op>/<int:units>', methods=['PUT'])
    def _user_data(user_name: str, op: str, units: int):
        try:
            return users.update_processing_units(user_name, op, units)
        except api.ApiError as e:
            return e.response

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
