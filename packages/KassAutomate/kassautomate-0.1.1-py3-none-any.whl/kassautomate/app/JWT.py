from flask import Flask, jsonify


class JWT:
    def __init__(self, jwt):
        self.jwt = jwt

    def jwt_configs(self):

        @self.jwt.token_in_blocklist_loader
        def check_if_token_in_blocklist(jwt_header, jwt_payload):
            # jti = jwt_payload["jti"]
            # token = TokenBlockList().where({"token":jti}).first()
            # print(token)
            # return token is not [None]
            return [None]

        @self.jwt.revoked_token_loader
        def revoke_token_callback(jwt_header, jwt_payload):
            print(jwt_header, jwt_payload)
            return (jsonify({"message": "token has revoked"}), 401)

        @self.jwt.expired_token_loader
        def expired_token_callback(jwt_header, jwt_payload):
            return (jsonify({"message": "token expired"}), 401)

        @self.jwt.needs_fresh_token_loader
        def token_not_refresh_callback(jwt_header, jwt_payload):
            return (
                jsonify({"message": "token not fresh. A new token is required"}),
                401,
            )

        @self.jwt.invalid_token_loader
        def invalid_token_callback(error):
            return (jsonify({"message": "token invalid"}), 401)

        @self.jwt.unauthorized_loader
        def missing_token_callback(error):
            return (jsonify({"message": "token is missing"}), 401)
