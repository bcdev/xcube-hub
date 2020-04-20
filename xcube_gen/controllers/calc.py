from xcube_gen.api import get_request_entry
from xcube_gen.types import AnyDict


def calc_cube_sizes_and_cost(processing_request: AnyDict):
    cube_config = get_request_entry(processing_request, 'cube_config',
                                    value_type=dict)
    x1, y1, x2, y2 = get_request_entry(cube_config, 'geometry',
                                       value_type=list,
                                       item_count=4,
                                       item_type=(int, float),
                                       path='cube_config')
    spatial_res = get_request_entry(cube_config, 'spatial_res',
                                    value_type=(int, float),
                                    path='cube_config')
    tile_width, tile_height = get_request_entry(cube_config, 'tile_size',
                                                value_type=str,
                                                item_count=2,
                                                item_type=int)
    start_date, end_date = get_request_entry(cube_config, 'time_range',
                                             value_type=list,
                                             item_count=2,
                                             item_type=str,
                                             path='cube_config')
    time_period = get_request_entry(cube_config, 'time_period',
                                    value_type=str,
                                    default_value='1D')
    band_names = get_request_entry(cube_config, 'band_names',
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
    date_range = pd.date_range(start=start_date, end=end_date, periods=time_period)
    num_times = len(date_range)

    return dict(size=[width, height],
                tile_size=[tile_width, tile_height],
                num_tiles=[num_tiles_x, num_tiles_y],
                num_times=num_times,
                num_variables=len(band_names))
