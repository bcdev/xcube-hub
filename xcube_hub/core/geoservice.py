from geo.Geoserver import Geoserver


def register(user_id, subscription, headers, raising):
    geo = Geoserver('http://127.0.0.1:8080/geoserver', username='admin', password='geoserver')
    geo.create_workspace(workspace='demo')
    geo.publish_featurestore(workspace='demo', store_name='geodb', pg_table='eea-urban-atlas_DE060L1_CELLE_UA2018')
    pass



