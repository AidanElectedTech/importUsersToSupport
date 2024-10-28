import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Database:
    def __init__(self, db_name):
        """
        Initialize the database connection using environment variables.
        """
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=db_name
            )

        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            self.connection = None

    def query(self, sql_query, params=None):
        """
        Execute a SQL query with optional parameters and return the result.
        
        :param sql_query: The SQL query string to execute.
        :param params: Optional parameters for the query (tuple or list).
        :return: Query result or None if an error occurs.
        """
        if self.connection is None:
            print("Not connected to the database")
            return None

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(sql_query, params)  # Execute the SQL query
            if (sql_query.startswith("SELECT")):
                result = cursor.fetchall()  # Fetch all the results
                return result  # Return the result of the query
            else:
                self.connection.commit()  # Commit changes for non-SELECT queries
                return cursor
        except Error as e:
            print(f"Error executing query: {e}")
            return None
        finally:
            cursor.close()  # Ensure the cursor is closed after the query

    def close(self):
        """
        Close the database connection.
        """
        if self.connection != None:
            if self.connection.is_connected():
                self.connection.close()

