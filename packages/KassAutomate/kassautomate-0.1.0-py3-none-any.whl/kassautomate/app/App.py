import base64
import os

from flask import Flask
from flask_jwt_extended import JWTManager

from kassautomate.app.Commands import Commands
from kassautomate.app.JWT import JWT


class App:
    def __init__(self) -> None:

        app = Flask(__name__)

        Commands(app).init()
        app = self.configs(app)

        self.app = app

    def configs(self, app):

        secret = os.getenv("FLASK_KEY", "")
        if secret == "":
            raise Exception("FLASK_KEY must be exists")

        app.config["JWT_ALGORITHM"] = "HS512"
        app.config["JWT_SECRET_KEY"] = base64.urlsafe_b64decode(os.getenv("FLASK_KEY"))

        return app

    @staticmethod
    def jwt(app):
        jwt = JWTManager(app)

        JWT(jwt).jwt_configs()

    def create_app(self):
        return self.app


create_app = App().create_app()
