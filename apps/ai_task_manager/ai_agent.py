
from functools import lru_cache
from urllib.parse import quote

from config import DB_PATH, GROQ_API_KEY, MODEL_NAME
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq


@lru_cache(maxsize=1)
def initialize_agent():

    database_uri = (
        f"sqlite:///file:{quote(str(DB_PATH))}"
        "?mode=ro&uri=true"
    )

    db = SQLDatabase.from_uri(database_uri)

    model = ChatGroq(
        model=MODEL_NAME,
        temperature=0,
        api_key=GROQ_API_KEY,
        streaming=False,
    )

    agent = create_sql_agent(
        llm=model,
        db=db,
        agent_type="tool-calling",
        verbose=False,
        prefix="""
        You are an AI assistant for a task management application.

        Rules:
        1. Only answer questions about the tasks database.
        2. Only perform SELECT queries.
        3. Never execute INSERT, UPDATE, DELETE, DROP,
           ALTER, CREATE, or other modifying statements.
        4. Never attempt to modify the database schema.
        5. Use only the tasks table.
        6. Do not expose sensitive system information.
        7. Keep answers concise and understandable.
        8. If the question is unrelated to tasks,
           politely explain your scope.
        """,
        max_iterations=5,
        max_execution_time=30,
    )

    return agent


def ask_ai(question):

    if not question or not question.strip():
        raise ValueError("Please enter a question.")

    if len(question) > 1000:
        raise ValueError("Question is too long.")

    agent = initialize_agent()

    response = agent.invoke({
        "input": question.strip()
    })

    return response["output"]
