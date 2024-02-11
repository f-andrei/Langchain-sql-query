from langchain.agents import AgentExecutor, Tool, ZeroShotAgent
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from model_tools import DatabaseInfo, DatabasePath, QueryData
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

model = ChatOpenAI(model="gpt-3.5-turbo-0125", verbose=True, api_key=OPENAI_API_KEY)

db_fname = DatabasePath()
dbinfo = DatabaseInfo()
querydata = QueryData()

tools = [
    Tool(
        name="DatabasePath",
        func=db_fname.run,
        description="Useful to find the file name of an SQLITE3 file. usually the file ends with '.db' and is a single word."
    ),
    Tool(
        name="DatabaseInfo",
        func=dbinfo.run,
        description="Useful to get the structure of an sqlite database, such as table names and columns."
    ),
    Tool(
        name="QueryData",
        func=querydata.run,
        description="Useful generate SQLite query"
    )
]

prefix = """Assist a human by answering the following questions as best you can. You have access to the following tools:"""
suffix = """Begin!"

{chat_history}
Question: {input}
{agent_scratchpad}"""

prompt = ZeroShotAgent.create_prompt(
    tools,
    prefix=prefix,
    suffix=suffix,
    input_variables=["input", "chat_history", "agent_scratchpad"],
)

memory = ConversationBufferMemory(memory_key="chat_history")

llm_chain = LLMChain(llm=model, prompt=prompt)
agent = ZeroShotAgent(llm_chain=llm_chain, tools=tools, verbose=True, handle_parsing_error=True)

agent_chain = AgentExecutor.from_agent_and_tools(
    agent=agent, tools=tools, verbose=True, memory=memory,
)
agent_chain.handle_parsing_errors = True

agent_chain.run(input="what is the movie count in the sakila db? what is the average house price in elite db? what is the average car price in elite db? answer one at a time")



