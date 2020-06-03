from xcube_gen import api
from xcube_gen.controllers.users import subtract_processing_units
from xcube_gen.utilities import EventHandler


class CallbackPut:
    def __init__(self):
        self.finished = EventHandler(self)


def trigger_punit_substract(sender, *args, **kwargs):
    if 'value' not in kwargs:
        raise api.ApiError(401, 'trigger_punit_substract could not be executed. Callback dict is missing')

    punits_requests = kwargs.get('values')['message']
    status = kwargs.get('values')['status']
    user_id = kwargs.get('user_id')

    if status == "CUBE_GENERATED":
        subtract_processing_units(user_id=user_id, punits_request=punits_requests)


PUT_EVENTS = CallbackPut()
PUT_EVENTS.finished += trigger_punit_substract
