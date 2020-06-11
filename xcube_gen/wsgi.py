from xcube_gen.service import new_app


app = new_app(static_folder='/home/xcube/viewer', cache_provider='leveldb')
