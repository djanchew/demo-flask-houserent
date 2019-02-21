from app import App

app = App.create_app()

if __name__ == "__main__":
    app.run(debug=app.config['DEBUG'], port=app.config['PORT'])
