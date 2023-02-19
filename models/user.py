from orator import Model

class User(Model):
    __primary_key__ = 'telegram_id'
    __fillable__ = ['telegram_id', 'age', 'status', 'opponent_id']
    pass
