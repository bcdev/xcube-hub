from xcube_gen.service import new_app


app = new_app(static_folder='/home/xcube/viewer')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)