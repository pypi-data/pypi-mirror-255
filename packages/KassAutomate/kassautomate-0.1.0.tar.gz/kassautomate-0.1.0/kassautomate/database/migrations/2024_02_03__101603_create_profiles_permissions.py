from KassOrm import Migration


class migrate(Migration):

    __type__ = "create"
    __table__ = "profiles_permissions"
    __comment__ = "Profiles and theirs permissions"

    def up(self):
        self.id().add()
        self.datetime("created_at").current_timestamp().add()
        self.bigIntegerUnisigned("profile_id").add()
        self.bigIntegerUnisigned("permmission_id").add()

        self.unique(["profile_id", "permmission_id"], "unq_prfl_perm").add()

    def down(self):
        self.dropTableIfExists()
