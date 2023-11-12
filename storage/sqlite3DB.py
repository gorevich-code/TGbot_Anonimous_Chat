import sqlite3
from sqlite3 import Error
from typing import Union


class SQLiteDB:
    def __init__(self, db_name) -> None:
        self.db_name = db_name
        self.table_name = None
        self.table_columns = None

    def create_connection(self):
        """Creates connection to DB"""
        connection = None
        database_path_name = f"./{self.db_name}.db"
        try:
            connection = sqlite3.connect(database_path_name)
            print("Connection to SQLite DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")

        return connection

    def execute_query(self, query: str):
        """Executes query to DB"""
        connection = self.create_connection()
        cursor = connection.cursor()

        try:
            cursor.execute(query)
            recieved_data = cursor.fetchall()
            print(f'recieved_data: {recieved_data}')
            connection.commit()
            print("Query executed successfully")

        except Error as e:
            print(f"The error '{e}' occurred")
        finally:
            if recieved_data:
                recieved_data = recieved_data.copy()
            if (connection):
                connection.close()
                print("SQL connection closed")
            return recieved_data
            

    def create_table(self, table_name, table_columns):
        self.table_name = table_name
        self.table_columns = table_columns
        table_columns = ', '.join(self.table_columns)
        query = f"CREATE TABLE if not exists {self.table_name}({table_columns});"
        self.execute_query(query)

    def _get_formatted_table_columns_data(self) -> str:
        """ Helper method which converts raw table columns data to string 
        with columns names with comma between except autofill 'id' column
        
        """

        return ", ".join(
            tuple(x.split(' ')[0] for x in self.table_columns[1::])
        )

    def insert_data(self, data):
        """Method to insert data into DB"""

        table_columns = self._get_formatted_table_columns_data()

        query = f"""
        INSERT INTO {self.table_name} ({table_columns})
        VALUES ({data})
        RETURNING id;
        """
        last_inserted_id = self.execute_query(query)
        return last_inserted_id
    
    def get_data_by_user_id(self, user_id: Union[int, str]):
        """Method to get data from DB by ID"""

        table_columns = self._get_formatted_table_columns_data()
        query = f"""
        SELECT {table_columns} FROM {self.table_name} 
        WHERE {user_id} IN (user1, user2)
        """
        recieved_data = self.execute_query(query)
        return recieved_data
    
    def delete_data_by_user_id(self, user_id: Union[int, str]):
        """Method to delete data from DB by ID"""

        query = f"""
        DELETE FROM {self.table_name} 
        WHERE {user_id} IN (user1, user2)
        """
        recieved_data = self.execute_query(query)
        return recieved_data


db = SQLiteDB(db_name='BotStorage')
db.create_table(
    table_name='Storage',
    table_columns=('id INTEGER UNIQUE PRIMARY KEY', 'user1 INTEGER', 'user2 INTEGER')
)

