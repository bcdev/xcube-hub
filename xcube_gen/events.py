from xcube_gen import api
from xcube_gen.api import get_json_request_value
from xcube_gen.controllers.users import subtract_processing_units
from xcube_gen.utilities import EventHandler


class PutEvents:
    finished = EventHandler("PutEvents")
    started = EventHandler("PutEvents")


class GetEvents:
    finished = EventHandler("GetEvents")
    started = EventHandler("GetEvents")


class DeleteEvents:
    finished = EventHandler("DeleteEvents")
    started = EventHandler("DeleteEvents")


def trigger_punit_substract(*args, **kwargs) -> None:
    if 'value' not in kwargs:
        raise api.ApiError(401, 'trigger_punit_substract could not be executed. Callback dict is missing')

    status = get_json_request_value(kwargs.get('value'), 'status', value_type=str)

    if status == "CUBE_GENERATED":
        user_id = kwargs.get('user_id')
        punits_requests = get_json_request_value(kwargs.get('value'), 'values', value_type=dict)
        subtract_processing_units(user_id=user_id, punits_request=punits_requests)


PutEvents.finished += trigger_punit_substract
