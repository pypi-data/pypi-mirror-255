from KassOrm import Migration


class migrate(Migration):

    __type__ = "create"
    __table__ = "users"
    __comment__ = "Users data"

    def up(self):
        self.id().add()
        self.datetime("created_at").current_timestamp().add()
        self.datetime("updated_at").current_timestamp().update_timestamp().add()
        self.string("name").add()
        self.string("login").unique().add()
        self.string("password").add()

    def down(self):
        self.dropTableIfExists()
