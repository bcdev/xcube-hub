import logging

import connexion
from flask_testing import TestCase

from xcube_hub.encoder import JSONEncoder


class BaseTestCase(TestCase):

    def create_app(self):
        logging.getLogger('connexion.operation').setLevel('ERROR')
        app = connexion.App(__name__, specification_dir='../xcube_hub/resources/')
        app.app.json_encoder = JSONEncoder
        app.add_api('openapi.yaml')
        return app.app
