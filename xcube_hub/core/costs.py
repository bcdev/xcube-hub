from typing import Dict

from xcube_hub import api
from xcube_hub.api import get_json_request_value
from xcube_hub.typedefs import JsonObject, Number


def _square(x: int) -> int:
    return x * x


SH_INPUT_PIXELS_PER_PUNIT = _square(512)
CCI_INPUT_PIXELS_PER_PUNIT = _square(768)
OUTPUT_PIXELS_PER_PUNIT = _square(512)

SH_INPUT_PUNITS_WEIGHT = 1.0
CCI_INPUT_PUNITS_WEIGHT = 1.0
OUTPUT_PUNITS_WEIGHT = 1.0


def _get_dim(dims: Dict, tgt: str, tgt_alt: str):
    try:
        res = get_json_request_value(dims, tgt,
                                     value_type=Number)
    except api.ApiError:
        try:
            res = get_json_request_value(dims, tgt_alt, value_type=Number)
        except api.ApiError:
            raise api.ApiError(400, "Cannot find a valid spatial dimension.")

    return res


def _check_lower_bound(value: Number, bound: Number = 0):
    if value <= bound:
        raise api.ApiError(400, f'Value must be greater than {bound}')


def get_size_and_cost(processing_request: JsonObject, datastore: JsonObject) -> JsonObject:
    dataset_descriptor = get_json_request_value(processing_request, 'dataset_descriptor',
                                                value_type=dict,
                                                item_type=dict)

    data_vars = get_json_request_value(dataset_descriptor, 'data_vars',
                                       value_type=dict,
                                       item_type=dict)

    num_variables = len(data_vars.keys())
    if num_variables == 0:
        raise api.ApiError(400, "Number of variables must be greater than 0.")

    dims = get_json_request_value(dataset_descriptor, 'dims',
                                  value_type=dict,
                                  item_type=dict)

    time = get_json_request_value(dims, 'time',
                                  value_type=int)

    lat = _get_dim(dims, 'lat', 'y')
    lon = _get_dim(dims, 'lon', 'x')

    size_estimation = get_json_request_value(processing_request, 'size_estimation',
                                             value_type=dict,
                                             item_type=dict)

    cost_params = get_json_request_value(datastore, 'cost_params',
                                         value_type=dict,
                                         item_type=dict)

    scheme = get_json_request_value(cost_params, 'scheme',
                                    value_type=str,
                                    item_type=dict,
                                    default_value='punits')

    input_pixels_per_punit = 1
    input_punits_weight = 0
    output_pixels_per_punit = 1
    output_punits_weight = 0

    if scheme != 'free':
        input_pixels_per_punit = get_json_request_value(cost_params, 'input_pixels_per_punit',
                                                        value_type=int)

        _check_lower_bound(input_pixels_per_punit, 0)

        input_punits_weight = get_json_request_value(cost_params, 'input_punits_weight',
                                                     value_type=float,
                                                     default_value=1.0)

        _check_lower_bound(input_punits_weight, 0)

        output_pixels_per_punit = get_json_request_value(cost_params, 'output_pixels_per_punit',
                                                         value_type=int)

        _check_lower_bound(output_pixels_per_punit, 0)

        output_punits_weight = get_json_request_value(cost_params, 'output_punits_weight',
                                                      value_type=float,
                                                      default_value=1.0)

        _check_lower_bound(output_punits_weight, 0)

    input_punits_count = _punits(lat, lon, time, num_variables, input_pixels_per_punit)
    output_punits_count = _punits(lat, lon, time, num_variables, output_pixels_per_punit)
    total_punits_count = round(max(input_punits_weight * input_punits_count,
                                   output_punits_weight * output_punits_count))

    return dict(dataset_descriptor=dataset_descriptor,
                size_estimation=size_estimation,
                data_store=datastore,
                punits=dict(input_count=input_punits_count,
                            input_weight=input_punits_weight,
                            output_count=output_punits_count,
                            output_weight=output_punits_weight,
                            total_count=total_punits_count))


def _punits(width: int, height: int, num_times: int, num_bands: int, pixels_per_punit: int) -> int:
    return num_bands * num_times * _idiv(width * height, pixels_per_punit)


def _idiv(x: int, y: int) -> int:
    return (x + y - 1) // y
