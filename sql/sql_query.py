# Import necessary libraries and modules
import langchain_community
from langchain.chains import create_sql_query_chain
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_community.utilities.sql_database import SQLDatabase
import pyodbc
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.callbacks import get_openai_callback
from langchain_community.agent_toolkits.sql.prompt import SQL_FUNCTIONS_SUFFIX
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
import os
# Replace these values with your actual SQL Server credentials
server = 'LOCALHOST'
database = 'REALESTATE'
OPENAI_API_KEY = "sk-proj-HlzQnTbGrHupQ5IIBTyyT3BlbkFJi2jOsF0cluhi8vseaMht"


# Create the connection string
connection_string = f"mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"
db = SQLDatabase.from_uri(connection_string)

# Initialize the SQL database toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=ChatOpenAI(temperature=0, openai_api_key=OPENAI_API_KEY))

print(toolkit)

# Retrieve the context and tools from the toolkit
context = toolkit.get_context()
tools = toolkit.get_tools()

# Define the SQL suffix prompts
SQL_SUFFIX1 = """Begin!\n\nQuestion: {input}\nThought:I should look at the tables in the database to see what I can query. Then I should query the schema of the most relevant tables. Ensure the query includes joins if needed to gather data from multiple tables.\n{agent_scratchpad}"""

SQL_FUNCTIONS_SUFFIX1 = """ 
I need to perform the following steps to answer the user's query effectively and only use SQL Server database system.:

1. **Paraphrase the Question for Clarity**:
    - Rephrase the user's question to ensure clarity and capture the intent accurately.
    - if ask general question you respond with a general answer, for example, "hi" or "how are you."

2. **Identify Relevant Tables**:
    - Look at the tables in the database to identify which tables are relevant to the question.

3. **Query the Schema**:
    - Examine the schema of the relevant tables to understand their structure and relationships.

4. **Determine the Need for Joins**:
    - Assess whether the question requires combining data from multiple tables.
    - If joins are necessary, identify the keys and relationships to use in the join.

5. **Construct the SQL Query**:
    - Write the SQL query using SQL Server syntax.
    - Ensure the query includes joins if needed to gather data from multiple tables.

7. **Format the Results**:
    - Present the query results in a clear and understandable format for the user. After I got the query I should go to SQL Server to proceed with the query and give the output as ANSWER.

Proceeding with these steps will ensure that I accurately understand and process the user's query, including handling joins and using the appropriate SQL Server syntax.
"""

# Define the messages for the chat prompt template
messages = [
    HumanMessagePromptTemplate.from_template("{input}"),
    AIMessage(content=SQL_SUFFIX1 + SQL_FUNCTIONS_SUFFIX1),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
]

# Create and configure the chat prompt template
prompt = ChatPromptTemplate.from_messages(messages)
prompt = prompt.partial(**context)

# Import the necessary modules for creating the agent
from langchain.agents import create_openai_tools_agent
from langchain.agents.agent import AgentExecutor

# Initialize the language model
llm = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, openai_api_key=OPENAI_API_KEY)

# Create the agent using the language model, tools, and prompt
agent = create_openai_tools_agent(llm, tools, prompt)

# Define a function to execute the agent with a given message
def agent_execute(msq):
    agent_executor = AgentExecutor(
        agent=agent,
        tools=toolkit.get_tools(),
        verbose=True
    )
    return agent_executor.invoke({"input": msq})

# Example query execution
result = agent_execute("how are you?")
#Mean Final Prices of New York Location with 3 Bedrooms
#Comparing Capitalization Rates Across Property Types
#Properties Built Before 2000 in New York and Not Occupied
#Categorizing House Ages and Calculating Average Final Price
#Getting Results for "Regex smith"
#The Second Highest Final Price (Profit)
#Counting Houses According to Price Categorization
#I WANT THE HIGHEST MONTHLY SALARY?
#Calculates the total monthly salary and total current debts for each buyer.
#Total Rental Income and Operating Expenses by Location
#Properties with High Return on Investment