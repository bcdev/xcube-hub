import os

from xcube_hub_old.service import new_app


def attach():
    if os.environ.get('WERKZEUG_RUN_MAIN') and os.environ.get('XCUBE_HUB_DEBUG'):
        import pydevd_pycharm
        pydevd_pycharm.settrace('0.0.0.0', port=9000, stdoutToServer=True, stderrToServer=True)


def new_wsgi_app():
    cache_provider = os.getenv('XCUBE_HUB_CACHE_PROVIDER') or 'leveldb'
    static_folder = os.getenv('XCUBE_API_STATIC_FOLDER') or '/home/xcube/viewer'
    attach()

    return new_app(static_folder=static_folder, cache_provider=cache_provider)


if __name__ == '__main__':
    app = new_wsgi_app()
    app.run(port=8000, host='0.0.0.0')
