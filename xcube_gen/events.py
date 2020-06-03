from xcube_gen import api
from xcube_gen.api import get_json_request_value
from xcube_gen.controllers.users import subtract_processing_units
from xcube_gen.utilities import EventHandler


class CallbackPut:
    def __init__(self):
        self.finished = EventHandler(self)


class CallbackGet:
    def __init__(self):
        self.finished = EventHandler(self)


class CallbackDelete:
    def __init__(self):
        self.finished = EventHandler(self)


def trigger_punit_substract(sender, *args, **kwargs):
    if 'value' not in kwargs:
        raise api.ApiError(401, 'trigger_punit_substract could not be executed. Callback dict is missing')

    status = get_json_request_value(kwargs.get('value'), 'status', value_type=str)

    if status == "CUBE_GENERATED":
        user_id = kwargs.get('user_id')
        punits_requests = get_json_request_value(kwargs.get('value'), 'values', value_type=dict)
        subtract_processing_units(user_id=user_id, punits_request=punits_requests)


CALLBACK_PUT_EVENTS = CallbackPut()
CALLBACK_PUT_EVENTS.finished += trigger_punit_substract

CALLBACK_GET_EVENTS = CallbackGet()

CALLBACK_DELETE_EVENTS = CallbackDelete()
