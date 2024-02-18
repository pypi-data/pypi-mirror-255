from KassOrm import Modelr

from kassautomate.database.models.Permission import Permission


class User(Modelr):

    __table__ = "users"

    def permissions(self):
        return self.hasManyToMany(
            Permission,
            "id",
            "id",
            "permission_id",
            "users_permissions",
            "user_id",
            "id",
        )
