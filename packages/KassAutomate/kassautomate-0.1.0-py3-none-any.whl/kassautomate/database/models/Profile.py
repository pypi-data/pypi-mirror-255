from KassOrm import Modelr

from kassautomate.database.models.Permission import Permission


class Profile(Modelr):

    __table__ = "profiles"

    def permissions(self):
        return self.hasManyToMany(
            Permission,
            "id",
            "id",
            "permission_id",
            "profiles_permissions",
            "profile_id",
            "id",
        )
