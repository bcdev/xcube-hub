from xcube_gen.api import get_json_request_value
from xcube_gen.types import JsonObject


def calc_processing_units(processing_request: JsonObject) -> JsonObject:
    cube_config = get_json_request_value(processing_request, 'cube_config',
                                         value_type=dict)
    x1, y1, x2, y2 = get_json_request_value(cube_config, 'geometry',
                                            value_type=list,
                                            item_count=4,
                                            item_type=(int, float),
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
    width = round((x2 - x1) / spatial_res)
    if width < 1.5 * tile_width:
        num_tiles_x = 1
        tile_width = width
    else:
        num_tiles_x = (width + tile_width - 1) // tile_width
        width = num_tiles_x * tile_width

    height = round((y2 - y1) / spatial_res)
    if height < 1.5 * tile_height:
        num_tiles_y = 1
        tile_height = height
    else:
        num_tiles_y = (height + tile_height - 1) // tile_height
        height = num_tiles_y * tile_height

    import pandas as pd
    date_range = pd.date_range(start=start_date, end=end_date, freq=time_period)
    num_times = len(date_range)

    # TODO
    processing_units_input_count = 0
    processing_units_output_count = 0
    processing_units_total_count = processing_units_input_count + processing_units_output_count

    return dict(sizeEstimation=dict(dims=dict(time=num_times, y=height, x=width),
                                    size=[width, height],
                                    tileSize=[tile_width, tile_height],
                                    tileCount=[num_tiles_x, num_tiles_y],
                                    variableCount=len(band_names)),
                processingUnits=dict(inputCount=processing_units_input_count,
                                     outputCount=processing_units_output_count,
                                     totalCount=processing_units_total_count))
