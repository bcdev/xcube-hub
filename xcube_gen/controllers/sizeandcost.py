from xcube_gen.api import get_json_request_value, ApiError
from xcube_gen.xg_types import JsonObject


def _square(x: int) -> int:
    return x * x


SH_INPUT_PIXELS_PER_PUNIT = _square(512)
CCI_INPUT_PIXELS_PER_PUNIT = _square(768)
OUTPUT_PIXELS_PER_PUNIT = _square(512)

SH_INPUT_PUNITS_WEIGHT = 1.0
CCI_INPUT_PUNITS_WEIGHT = 1.0
OUTPUT_PUNITS_WEIGHT = 1.0


def get_size_and_cost(processing_request: JsonObject) -> JsonObject:
    input_config = get_json_request_value(processing_request, 'input_config',
                                          value_type=dict)
    datastore_id = get_json_request_value(input_config, 'datastore_id',
                                          value_type=str,
                                          key_path='input_config')
    cube_config = get_json_request_value(processing_request, 'cube_config',
                                         value_type=dict)
    x1, y1, x2, y2 = get_json_request_value(cube_config, 'geometry',
                                            value_type=list,
                                            item_count=4,
                                            item_type=(int, float),
                                            key_path='cube_config')
    crs = get_json_request_value(cube_config, 'crs',
                                 value_type=str,
                                 key_path='cube_config')
    spatial_res = get_json_request_value(cube_config, 'spatial_res',
                                         value_type=(int, float),
                                         key_path='cube_config')
    tile_width, tile_height = get_json_request_value(cube_config, 'tile_size',
                                                     value_type=list,
                                                     item_count=2,
                                                     item_type=int)
    start_date, end_date = get_json_request_value(cube_config, 'time_range',
                                                  value_type=list,
                                                  item_count=2,
                                                  item_type=str,
                                                  key_path='cube_config')
    time_period = get_json_request_value(cube_config, 'time_period',
                                         value_type=str,
                                         default_value='1D')
    band_names = get_json_request_value(cube_config, 'band_names',
                                        value_type=list,
                                        item_type=str,
                                        default_value=[])

    is_geo_crs = crs.lower() == 'epsg:4326' or crs.endswith('/4326') or crs.endswith('/WGS84')

    width = round((x2 - x1) / spatial_res)
    if width < 1.5 * tile_width:
        num_tiles_x = 1
        tile_width = width
    else:
        num_tiles_x = _idiv(width, tile_width)
        width = num_tiles_x * tile_width

    height = round((y2 - y1) / spatial_res)
    if height < 1.5 * tile_height:
        num_tiles_y = 1
        tile_height = height
    else:
        num_tiles_y = _idiv(height, tile_height)
        height = num_tiles_y * tile_height

    import pandas as pd
    date_range = pd.date_range(start=start_date, end=end_date, freq=time_period)

    num_times = len(date_range)
    num_variables = len(band_names)
    num_requests = num_variables * num_times * num_tiles_x * num_tiles_y
    num_bytes_per_pixel = 4  # float32 for all variables for time being
    num_bytes = num_variables * num_times * (height * width * num_bytes_per_pixel)

    if datastore_id == 'sentinelhub':
        input_pixels_per_punit = SH_INPUT_PIXELS_PER_PUNIT
        input_punits_weight = SH_INPUT_PUNITS_WEIGHT
    elif datastore_id == 'cciodp':
        input_pixels_per_punit = CCI_INPUT_PIXELS_PER_PUNIT
        input_punits_weight = CCI_INPUT_PUNITS_WEIGHT
    else:
        raise ApiError(400, f'unsupported "input_config/datastore_id" entry: "{datastore_id}"')

    output_pixels_per_punit = OUTPUT_PIXELS_PER_PUNIT
    output_punits_weight = OUTPUT_PUNITS_WEIGHT

    input_punits_count = _punits(width, height, num_times, num_variables, input_pixels_per_punit)
    output_punits_count = _punits(width, height, num_times, num_variables, output_pixels_per_punit)
    total_punits_count = round(max(input_punits_weight * input_punits_count,
                                   output_punits_weight * output_punits_count))

    x_name, y_name = ('lon', 'lat') if is_geo_crs else ('x', 'y')

    return dict(schema=dict(dims={'time': num_times, y_name: height, x_name: width},
                            image_size=[width, height],
                            tile_size=[tile_width, tile_height],
                            num_variables=num_variables,
                            num_tiles=[num_tiles_x, num_tiles_y],
                            num_requests=num_requests,
                            num_bytes=num_bytes),
                punits=dict(input_count=input_punits_count,
                            input_weight=input_punits_weight,
                            output_count=output_punits_count,
                            output_weight=output_punits_weight,
                            total_count=total_punits_count))


def _punits(width: int, height: int, num_times: int, num_bands: int, pixels_per_punit: int) -> int:
    return num_bands * num_times * _idiv(width * height, pixels_per_punit)


def _idiv(x: int, y: int) -> int:
    return (x + y - 1) // y
