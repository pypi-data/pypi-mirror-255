from KassOrm import Migration


class migrate(Migration):

    __type__ = "create"
    __table__ = "profiles"
    __comment__ = "Profiles data"

    def up(self):
        self.id().add()
        self.datetime("created_at").current_timestamp().add()
        self.string("name", 10).unique().add()
        self.string("description").add()

    def down(self):
        self.dropTableIfExists()
