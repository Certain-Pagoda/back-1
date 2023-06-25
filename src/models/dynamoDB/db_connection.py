## Iinit the database objects
from src.models.dynamoDB.users import User

class InitDB:
    
    def __init__(self):
        self.__init_tables()
    
    def __init_tables(self):
        if not User.exists():
            User.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)
