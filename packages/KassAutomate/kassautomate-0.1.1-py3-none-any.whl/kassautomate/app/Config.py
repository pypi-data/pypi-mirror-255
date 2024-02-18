from flask import current_app


class Config:

    @staticmethod
    def all():
        return current_app.config

    @staticmethod
    def get(key, default=""):
        if current_app.config[key]:
            return current_app.config[key]
        else:
            return default
