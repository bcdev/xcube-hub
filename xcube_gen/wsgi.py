import os

from xcube_gen.service import new_app


xcube_gen_debug_host = os.getenv('XCUBE_GEN_DEBUG_HOST')

if xcube_gen_debug_host:
    import pydevd_pycharm
    pydevd_pycharm.settrace(xcube_gen_debug_host, port=9000, stdoutToServer=True, stderrToServer=True)


def new_wsgi_app():
    cache_provider = os.getenv('XCUBE_API_CACHE_PROVIDER') or 'leveldb'
    static_folder = os.getenv('XCUBE_API_STATIC_FOLDER') or '/home/xcube/viewer'

    return new_app(static_folder=static_folder, cache_provider=cache_provider)


app = new_wsgi_app()


if __name__ == '__main__':
    app.run(port=8000, host='0.0.0.0')

