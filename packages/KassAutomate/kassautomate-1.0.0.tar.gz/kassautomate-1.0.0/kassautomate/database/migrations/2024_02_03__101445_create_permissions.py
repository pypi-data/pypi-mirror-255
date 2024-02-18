from KassOrm import Migration


class migrate(Migration):

    __type__ = "create"
    __table__ = "permissions"
    __comment__ = "App permissions"

    def up(self):
        self.id().add()
        self.datetime("created_at").current_timestamp().add()
        self.string("cod", 10).unique().add()
        self.string("description").add()

    def down(self):
        self.dropTableIfExists()
