from langchain.memory import ConversationBufferMemory
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
from utils import save_fname, load_fname
from queries import get_database_info
from typing import Type
import sqlite3

AVAILABLE_DATABASES = ['chinook.db', 'titanic.db', 'sakila.db', 'sample.db']

# Instantiate model's memory
memory = ConversationBufferMemory(memory_key="chat_history")


class DatabasePathInput(BaseModel):
    """Represents the input schema for the DatabasePath Tool.

    Attributes:
        filename (str): The name of the SQLite3 database file.
    """
    filename: str = Field(..., description="SQLITE3 file name")

class DatabasePath(BaseTool):
    """Tool to find the path or filename of a database.

    This tool retrieves the path or filename of a specified SQLite database.

    Attributes:
        name (str): The name of the tool.
        args_schema (Type[BaseModel]): The input schema for the tool.
        description (str): A brief description of the tool's functionality (important for the model).
    """
    name: str = "database_path"
    args_schema: Type[BaseModel] = DatabasePathInput
    description: str = f"""This function is useful to retrieve the file 
                        name of a SQLITE database. usually has a file 
                        extension of '.db' and is a single word. """
    
    def _run(self, filename: str) -> str:
        """
        Retrieve the path or filename of the specified SQLite database.

        Args:
            filename (str): The name of the SQLite database file.

        Returns:
            str: The path or filename of the SQLite database, or an error message if not found.

        Notes:
            This method retrieves the path or filename of the specified SQLite database.
            It checks if the provided filename already has the '.db' extension; if not,
            it adds the extension to ensure consistency. Then, it checks if the resulting
            filename matches any of the predefined database filenames in the AVAILABLE_DATABASES list.

            If the filename matches, it adds the user message to memory and saves the filename
            (with extension) to a JSON file. Finally, it returns the filename.

            If the filename does not match any of the predefined database filenames, it adds
            an appropriate error message to the model's memory and returns 'File not found.'.
        """
        try:
            database_path = filename.lower()
            # Check if filename already has the .db extension
            if not database_path.endswith('.db'):
                # If not, add the extension
                database_path_ext = database_path + '.db'
            else:
                database_path_ext = database_path
            
            # Check if the filename matches any of the database filenames
            if database_path_ext in AVAILABLE_DATABASES:
                # Add the user message to memory
                memory.chat_memory.add_user_message(database_path_ext)
                # Save the filename (with extension) to the JSON file
                save_fname(database_path_ext)
                return database_path_ext
            else:
                # If filename does not match any of the filenames in AVAILABLE_DATABASES, return 'File not found.'
                memory.chat_memory.add_ai_message('File not found.')
                return 'File not found.'
        except Exception as e:
            # Handle any unexpected errors and return an error message
            return f"Error occurred while retrieving database path: {e}"


class DatabaseInfoInput(BaseModel):
    """Represents the input schema for the DatabaseInfo Tool.

    Attributes:
        database_path (str): The path or filename of the SQLite3 database.
    """
    database_path: str = Field(..., description="SQLITE3 file name")

class DatabaseInfo(BaseTool):
    """Tool to retrieve information about a SQLite database.

    This tool retrieves information such as table names and column names from a specified SQLite database.

    Attributes:
        name (str): The name of the tool.
        args_schema (Type[BaseModel]): The input schema for the tool.
        description (str): A brief description of the tool's functionality (important for the model).
    """
    name: str = "database_info"
    args_schema: Type[BaseModel] = DatabaseInfoInput
    description: str = f"""This function is useful to retrieve the database 
                        structre of an SQLITE3, such as table names 
                        and columns."""
    
    def _run(self, database_path: str) -> str:
        """
        Retrieve information about the specified SQLite database.

        Args:
            database_path (str): The path or filename of the SQLite database.

        Returns:
            str: A formatted string containing information about the database's structure.

        Notes:
            The database filename is loaded using `load_fname()` for efficiency,
            which retrieves the filename previously obtained by the DatabasePath tool.
            This approach avoids passing the filename as a parameter, which could
            sometimes be lost and result in increased token consumption and longer
            response times when answering user queries.

            This method retrieves table names and column names from the SQLite database
            specified by `database_path`. It formats the retrieved information into a
            single string, where each line represents a table along with its associated
            column names. The formatted string is then added to the model's memory,
            allowing it to provide elaborated responses based on this information.
        """
        try:
            # Load existing filename retrieved earlier
            database_path = load_fname()
            if database_path not in AVAILABLE_DATABASES:
                return "Database file not found."
            # Retrives information (table names, column names) from a SQLite data base.
            database_schema_dict = get_database_info(database_path)
            if not database_schema_dict:
                return "No database schema information available."
            # Formats it as a single string. E.g. table_name: person, column_name: age
            database_schema_string = "\n".join(
               [
                   f"Table: {table['table_name']}\nColumns: {', '.join(table['column_name'])}"
                   for table in database_schema_dict
               ])
            # Adds the formatted string to the models memory, so it can elaborate on it.
            memory.chat_memory.add_ai_message(database_schema_string)
            return database_schema_string
        except Exception as e:
            return f"Error occurred while retrieving database information: {e}"


class QueryDataInput(BaseModel):
    """Represents the input schema for the QueryData Tool.

    Attributes:
        query (str): The SQLite3 query to execute.
    """
    query: str = Field(..., description="SQLite3 query (sql)")

    class Config:
        arbitrary_types_allowed = True

class QueryData(BaseTool):
    """Tool to query data from a SQLite3 database.

    This tool executes the provided SQLite3 query on the specified database and returns the results.

    Attributes:
        name (str): The name of the tool.
        args_schema (Type[BaseModel]): The input schema for the tool.
        description (str): A brief description of the tool's functionality (important for the model).
    """
    name: str = "query_data"    
    args_schema: Type[BaseModel] = QueryDataInput
    description: str =  f"""This function is useful to query data from the 
                        database. Generate a SQLITE3 query to answer the 
                        user's question."""          

    def _run(self, query) -> str:
        """
        Execute the provided SQL query on the SQLite database.

        Args:
            query (str): The SQL query to execute.

        Returns:
            str: A string representation of the query results.

        Notes:
            For efficiency, the database filename is loaded using `load_fname()`,
            which retrieves the filename previously obtained by the DatabasePath tool.
            This approach avoids passing the filename as a parameter, which could
            sometimes be lost and result in increased token consumption and longer
            response times when answering user queries.
        """
        database_path = load_fname()
        if database_path is None:
            return "Database file path is not available."
        try:
            with sqlite3.connect(database_path) as conn:
                results = str(conn.execute(query).fetchall())
                return results
        except sqlite3.Error as e:
            return f"Query failed with error: {e}"



