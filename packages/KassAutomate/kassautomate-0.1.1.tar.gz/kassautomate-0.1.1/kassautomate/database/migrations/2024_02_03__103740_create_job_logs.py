from KassOrm import Migration


class migrate(Migration):

    __type__ = "create"
    __table__ = "job_logs"
    __comment__ = "Lobs about jobs"

    def up(self):
        self.id().add()
        self.bigIntegerUnisigned("job_id").add()
        self.datetime("started_at").current_timestamp().add()
        self.datetime("finished_in").nullable().add()
        self.enum("success", ["1", "0"]).add()

    def down(self):
        self.dropTableIfExists()
