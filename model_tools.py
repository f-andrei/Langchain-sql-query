from langchain.memory import ConversationBufferMemory
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool
from utils import save_fname, load_fname
from queries import get_database_info
from typing import Type
import sqlite3

fnames = ['chinook.db', 'titanic.db', 'sakila.db', 'elite.db']

memory = ConversationBufferMemory(memory_key="chat_history")

class QueryDataInput(BaseModel):
    """Entrada para QueryData"""
    query: str = Field(..., description="SQLite3 query (sql)")

    class Config:
        arbitrary_types_allowed = True

class QueryData(BaseTool):
    """
    Função para coletar dados de um banco SQLITE
    com uma query SQL gerada pelo gpt
    """
    name: str = "query_data"    
    args_schema: Type[BaseModel] = QueryDataInput
    description: str =  f"""This function is useful to query data from the database. Generate a SQLITE3 query to answer
    the user's question."""                   

    def _run(self, query) -> str:
        database_path = load_fname()
        if database_path is None:
            return "Database file path is not available."
        try:
            with sqlite3.connect(database_path) as conn:
                results = str(conn.execute(query).fetchall())
                return results
        except sqlite3.Error as e:
            return f"Query failed with error: {e}"

class DatabasePathInput(BaseModel):
    """Retrives database structure (tables, columns)"""
    file_name: str = Field(..., description="SQLITE3 file name")

class DatabasePath(BaseTool):
    name: str = "database_path"
    args_schema: Type[BaseModel] = DatabasePathInput
    description: str = f"""This function is useful to retrieve the file name of a SQLITE database. usually has a file extension of '.db' and is a single word. """
    
    def _run(self, file_name: str) -> str:
        try:
            database_path = file_name.lower()
            
            # Check if file_name already has the .db extension
            if not database_path.endswith('.db'):
                # If not, add the extension
                database_path_ext = database_path + '.db'
            else:
                database_path_ext = database_path
            
            # Check if the file_name (with or without extension) matches any of the database filenames
            if database_path in fnames or database_path_ext in fnames:
                # Add the user message to memory
                memory.chat_memory.add_user_message(database_path_ext)
                # Save the filename (with extension) to the JSON file
                save_fname(database_path_ext)
                return database_path_ext
            else:
                # If file_name does not match any of the filenames in fnames, return 'File not found.'
                memory.chat_memory.add_ai_message('File not found.')
                return 'File not found.'
        except Exception as e:
            # Handle any unexpected errors and return an error message
            return f"Error occurred while retrieving database path: {e}"


class DatabaseInfoInput(BaseModel):
    """Retrives database structure (tables, columns)"""
    database_path: str = Field(..., description="SQLITE3 file name")

class DatabaseInfo(BaseTool):
    name: str = "database_info"
    args_schema: Type[BaseModel] = DatabaseInfoInput
    description: str = f"""This function is useful to retrieve the database structre of an SQLITE3,
                        such as table names and columns."""
    
    def _run(self, database_path: str) -> str:
        try:
            database_path = load_fname()
            if database_path not in fnames:
                return "Database file not found."
            database_schema_dict = get_database_info(database_path)
            if not database_schema_dict:
                return "No database schema information available."
            database_schema_string = "\n".join(
               [
                   f"Table: {table['table_name']}\nColumns: {', '.join(table['column_name'])}"
                   for table in database_schema_dict
               ])
            memory.chat_memory.add_ai_message(database_schema_string)
            return database_schema_string
        except Exception as e:
            return f"Error occurred while retrieving database information: {e}"
