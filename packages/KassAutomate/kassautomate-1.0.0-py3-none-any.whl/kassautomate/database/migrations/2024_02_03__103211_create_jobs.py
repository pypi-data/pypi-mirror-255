from KassOrm import Migration


class migrate(Migration):

    __type__ = "create"
    __table__ = "jobs"
    __comment__ = "Jobs data"

    def up(self):
        self.id().add()
        self.datetime("created_at").current_timestamp().add()
        self.datetime("updated_at").current_timestamp().update_timestamp().add()
        self.string("name").unique().add()
        self.enum("active", ["1", "0"]).add()

    def down(self):
        self.dropTableIfExists()
