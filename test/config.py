import kubernetes

SH_CFG = {
    "input_config": {
        "datastore_id": "sentinelhub"
    },
    "cube_config": {
        "dataset_name": "S2L1C",
        "variable_names": [
            "B04"
        ],
        "tile_size": [
            1024,
            1024
        ],
        "geometry": [
            7,
            53,
            9,
            55
        ],
        "spatial_res": 0.001,
        "crs": "http://www.opengis.net/def/crs/EPSG/0/4326",
        "time_range": [
            "2019-04-22",
            "2019-04-25"
        ],
        "time_period": "1D"
    },
    "output_config": {
        "path": "https://s3.amazonaws.com/eurodatacube-test/test.zarr",
        "provider_access_key_id": "ODNÖONKI",
        "provider_secret_access_key": "ädflsvkdsöfl"
    }
}


TEST_POD_RUNNING = kubernetes.client.V1Pod(
    metadata=kubernetes.client.V1ObjectMeta(name='helge-cate-running'),
    status=kubernetes.client.V1PodStatus(phase='Running')
)

TEST_POD_PENDING = kubernetes.client.V1Pod(
    metadata=kubernetes.client.V1ObjectMeta(name='helge-cate-pending'),
    status=kubernetes.client.V1PodStatus(phase='Pending')
)

TEST_POD_TERMINATING = kubernetes.client.V1Pod(
    metadata=kubernetes.client.V1ObjectMeta(name='helge-cate-terminating'),
    status=kubernetes.client.V1PodStatus(phase='Terminating')
)

TEST_PODS = kubernetes.client.V1PodList(items=[TEST_POD_RUNNING, TEST_POD_PENDING, TEST_POD_TERMINATING])
TEST_PODS_EMPTY = kubernetes.client.V1PodList(items=[])
