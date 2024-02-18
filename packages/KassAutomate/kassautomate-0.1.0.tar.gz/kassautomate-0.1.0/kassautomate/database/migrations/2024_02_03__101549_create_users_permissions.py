from KassOrm import Migration


class migrate(Migration):

    __type__ = "create"
    __table__ = "users_permissions"
    __comment__ = "Users and his permissions"

    def up(self):
        self.id().add()
        self.datetime("created_at").current_timestamp().add()
        self.bigIntegerUnisigned("user_id").add()
        self.bigIntegerUnisigned("permmission_id").add()

        self.unique(["user_id", "permmission_id"], "unq_user_perm")

    def down(self):
        self.dropTableIfExists()
