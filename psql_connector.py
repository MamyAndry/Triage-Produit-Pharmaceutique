import psycopg2
from psycopg2 import sql

class PostgreSQLConnection:
    def __init__(self, host="localhost", database="pharmacie", user="mamisoa", password="prom15", port="5432"):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.connection = None
        self.cursor = None

    def connect(self):
        """Establishes a connection to the PostgreSQL server."""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password,
                port=self.port
            )
            self.cursor = self.connection.cursor()
            print("Connection to PostgreSQL established successfully.")
        except Exception as error:
            print("Error while connecting to PostgreSQL:", error)
    def execute_query(self, query, fetch_one=False, fetch_results=True):
        """
        Executes a given SQL query. Can handle fetching and modifying queries.
        
        Parameters:
        - query: The SQL query to execute.
        - fetch_one: If True, fetch one record (only applicable if fetch_results is True).
        - fetch_results: If True, fetch results (useful for SELECT queries). If False, execute the query without fetching (useful for INSERT, UPDATE, DELETE).
        
        Returns:
        - If fetch_results is True:
        - If fetch_one is True, returns a single record.
        - If fetch_one is False, returns all records.
        - If fetch_results is False, returns the number of rows affected by the query.
        """
        try:
            # Execute the query
            self.cursor.execute(query)
            
            # Commit changes for insert/update/delete queries
            if not fetch_results and not fetch_one:
                self.connection.commit()
                return self.cursor.rowcount  # Number of rows affected
            
            # Fetch results for SELECT queries
            if fetch_one:
                result = self.cursor.fetchone()
            else:
                result = self.cursor.fetchall()
            
            return result
        
        except Exception as error:
            print("Error while executing query:", error)
            return None


    def close(self):
        """Closes the cursor and the connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("PostgreSQL connection closed.")
