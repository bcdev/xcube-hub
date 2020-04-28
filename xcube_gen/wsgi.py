from .service import new_app

app = new_app()

if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', port=80, debug=True)
else:
    application = app
