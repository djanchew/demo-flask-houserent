from flask import Flask
# from app.models.user import db
from flask_pymongo import PyMongo


class App:

    @classmethod
    def create_app(cls):
        cls.app = Flask(__name__)

        cls.app.config.from_object('app.settings')
        cls.app.config.from_object('app.secure')

        cls.register_blueprint(cls.app)

        cls.mongo = PyMongo(cls.app)

        return cls.app

    @staticmethod
    def register_blueprint(app):
        from .views import view
        app.register_blueprint(view)
