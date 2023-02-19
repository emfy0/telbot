from orator.migrations import Migration


class CreateUsersTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('users') as table:
            table.integer('telegram_id')
            table.integer('opponent_id').nullable(True)
            table.integer('age').nullable(True)
            table.text('status').nullable(True)
            # ...
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('users')
