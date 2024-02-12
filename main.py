from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, Tool, ZeroShotAgent
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from model_tools import DatabaseInfo, DatabasePath, QueryData
from dotenv import load_dotenv
from utils import save_fname, log_chat_history
import os

# Load environment variables
load_dotenv()

# Retrieve OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_KEY")

# Initialize the ChatOpenAI object with the desired model
#model = ChatOpenAI(model="gpt-4-turbo-preview", api_key=OPENAI_API_KEY) # best model (but expensive)
model = ChatOpenAI(model="gpt-3.5-turbo", api_key=OPENAI_API_KEY)


# Instantiate tools for database operations
db_path = DatabasePath()
db_info = DatabaseInfo()
query_data = QueryData()

# Define tools available for the model
tools = [
    Tool(
        name="DatabasePath",
        func=db_path.run,
        description="Useful to find the file name of an SQLITE3 file. usually the file ends with '.db' and is a single word."
    ),
    Tool(
        name="DatabaseInfo",
        func=db_info.run,
        description="Useful to get the structure of an sqlite database, such as table names and columns."
    ),
    Tool(
        name="QueryData",
        func=query_data.run,
        description="Useful to query data from a structural database. Takes only the SQL query."
    )
]

# Define prefix and suffix for model prompts
prefix = """Assist a human by answering the following questions as best you can. 
If there are more than one question, after answering the first, start from the beginning again.
Remember for each question you have to first find the database filename, then its information,
finally execute the SQL query.
You have access to the following tools"""
suffix = """Begin!"

{chat_history}
Question: {input}
{agent_scratchpad}"""

# Create prompt for the ZeroShotAgent
prompt = ZeroShotAgent.create_prompt(
    tools,
    prefix=prefix,
    suffix=suffix,
    input_variables=["input", "chat_history", "agent_scratchpad"],
)

# Instantiate model's memory
memory = ConversationBufferMemory(memory_key="chat_history", input_key='input', output_key="output")

# Create LLMChain with the model and prompt
llm_chain = LLMChain(llm=model, prompt=prompt)

# Instantiate ZeroShotAgent with LLMChain and tools
agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools)

# Create AgentExecutor from agent and tools
agent_chain = AgentExecutor.from_agent_and_tools(
    agent=agent, tools=tools, verbose=True, memory=memory,
)
# Set return_intermediate_steps to True (returns the model's thought process as dict)
agent_chain.return_intermediate_steps = True
# Set parsing errors handling
agent_chain.handle_parsing_errors = True

# Clear previous database path
save_fname('')

# Define sample questions
question = """what is the movie count in the sakila database? 
what is the average house price in sample database? 
what is the average car price in sample database?"""

# Invoke agent to answer the questions
message = agent_chain.invoke(input=question)

# Load chat history from memory (user input and final answer)
chat_history = memory.load_memory_variables({})

intermediate_steps = message["intermediate_steps"]

# Log the chat history and intermediate steps
log_chat_history(chat_history, intermediate_steps)