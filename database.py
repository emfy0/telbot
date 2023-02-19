from orator import DatabaseManager
from orator import Model

def initialize_db():
    config = {
        'sqlite': {
            'driver': 'sqlite',
            'database': './database.db',
        }
    }

    db = DatabaseManager(config)
    Model.set_connection_resolver(db)
