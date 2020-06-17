from xcube_gen import api
from xcube_gen.api import get_json_request_value
from xcube_gen.cache import Cache
from xcube_gen.controllers.sizeandcost import get_size_and_cost
from xcube_gen.controllers.users import subtract_processing_units
from xcube_gen.utilities import EventHandler


class PutEvents:
    finished = EventHandler("PutEvents")
    started = EventHandler("PutEvents")


class GetEvents:
    finished = EventHandler("GetEvents")
    started = EventHandler("GetEvents")
    errored = EventHandler("GetEvents")


class DeleteEvents:
    finished = EventHandler("DeleteEvents")
    started = EventHandler("DeleteEvents")


def trigger_punit_substract(*args, **kwargs) -> bool:
    if 'value' not in kwargs:
        raise api.ApiError(401, 'System error (trigger_punit_substract): Callback dict is missing.')

    if 'job_id' not in kwargs:
        raise api.ApiError(401, 'System error (trigger_punit_substract): job_id is missing.')

    if 'user_id' not in kwargs:
        raise api.ApiError(401, 'System error (trigger_punit_substract): user_id is missing.')

    status = get_json_request_value(kwargs.get('value'), 'status', value_type=str)

    if status == "CUBE_GENERATED":
        user_id = kwargs.get('user_id')
        job_id = kwargs.get('job_id')

        cache = Cache()
        processing_request = cache.get(job_id)

        if processing_request:
            punits_requests = get_size_and_cost(processing_request=processing_request)
            subtract_processing_units(user_id=user_id, punits_request=punits_requests)
        else:
            raise api.ApiError(401, "System error (trigger_punit_substract): Could not find job.")
    else:
        raise api.ApiError(401, "System error (trigger_punit_substract): Job status has to be CUBE_GENERATED before "
                                "I can substract punits.")

    return True


PutEvents.finished += trigger_punit_substract
