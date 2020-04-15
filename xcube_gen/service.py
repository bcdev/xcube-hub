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
from xcube_gen.api import job, jobs, info, job_delete, jobs_purge, job_status, job_result, main


def new_app():
    """Create the service app."""
    app = flask.Flask('xcube-genserv')
    flask_cors.CORS(app)

    @app.route('/job', methods=['POST'])
    def _job():
        return job(flask.request.json)

    @app.route('/jobs', methods=['GET'])
    def _jobs():
        return jobs()

    @app.route('/delete', methods=['DELETE'])
    def _delete():
        return job_delete(flask.request.json)

    @app.route('/purge', methods=['DELETE'])
    def _purge():
        return jobs_purge(flask.request.json)

    @app.route('/status/<job_name>', methods=['GET'])
    def _status(job_name):
        return job_status(job_name)

    @app.route('/result/<job_name>', methods=['GET'])
    def _result(job_name):
        return job_result(job_name)

    @app.route('/info', methods=['GET'])
    def _info():
        return info()

    @app.route('/', methods=['GET'])
    def _main():
        return main()

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
