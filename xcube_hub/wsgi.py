import os

from xcube_hub.service import new_app


def new_wsgi_app():
    cache_provider = os.getenv('XCUBE_API_CACHE_PROVIDER') or 'leveldb'
    static_folder = os.getenv('XCUBE_API_STATIC_FOLDER') or '/home/xcube/viewer'

    return new_app(static_folder=static_folder, cache_provider=cache_provider)


app = new_wsgi_app()


if __name__ == '__main__':
    app.run(port=8000, host='0.0.0.0')

