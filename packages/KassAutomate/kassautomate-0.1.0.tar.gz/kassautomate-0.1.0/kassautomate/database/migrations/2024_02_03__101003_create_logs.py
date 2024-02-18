from KassOrm import Migration


class migrate(Migration):

    __type__ = "create"
    __table__ = "logs"
    __comment__ = "App logs"

    def up(self):
        self.id().add()
        self.datetime("created_at").current_timestamp().add()
        self.string("title").add()
        self.text("log").add()

    def down(self):
        self.dropTableIfExists()
