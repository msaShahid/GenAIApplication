import sqlite3

import streamlit as st
from dotenv import load_dotenv
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq

load_dotenv()

DB_PATH = "tasks.db"


def initialize_database():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'Pending',
            priority TEXT DEFAULT 'Medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    conn.commit()
    conn.close()


@st.cache_resource
def initialize_agent():

    initialize_database()

    model = ChatGroq(model="openai/gpt-oss-20b", temperature=0, streaming=True)

    db = SQLDatabase.from_uri("sqlite:///tasks.db")

    agent = create_sql_agent(llm=model, db=db, agent_type="tool-calling", verbose=True)

    return agent


def add_task(title, description, priority):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO tasks (title, description, priority)
        VALUES (?, ?, ?)
    """,
        (title, description, priority),
    )

    conn.commit()
    conn.close()


def get_tasks():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks ORDER BY id DESC")

    tasks = cursor.fetchall()

    conn.close()

    return tasks


def update_task(task_id, status):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET status = ?
        WHERE id = ?
        """,
        (status, task_id),
    )

    conn.commit()
    conn.close()


def delete_task(task_id):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    conn.commit()
    conn.close()


st.set_page_config(page_title="AI Task Manager", page_icon="📋", layout="wide")

st.title("📋 AI Database Task Manager")

st.caption("Streamlit + SQLite + Groq AI Agent")

initialize_database()

st.sidebar.header("➕ Create New Task")

title = st.sidebar.text_input("Task Title")

description = st.sidebar.text_area("Description")

priority = st.sidebar.selectbox("Priority", ["Low", "Medium", "High"])

if st.sidebar.button("Add Task"):

    if title.strip():

        add_task(title, description, priority)

        st.sidebar.success("Task added successfully!")

        st.rerun()

    else:
        st.sidebar.warning("Enter a task title.")



st.subheader("📌 All Tasks")

tasks = get_tasks()

if tasks:

    for task in tasks:

        task_id, title, description, status, priority, created_at = task

        with st.expander(f"{task_id}. {title} — {status}"):

            st.write("Description:", description)

            st.write("Priority:", priority)

            st.write("Created:", created_at)

            new_status = st.selectbox(
                "Update Status",
                ["Pending", "In Progress", "Completed"],
                index=["Pending", "In Progress", "Completed"].index(status),
                key=f"status_{task_id}",
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button("Update Task", key=f"update_{task_id}"):

                    update_task(task_id, new_status)

                    st.success("Task updated!")

                    st.rerun()

            with col2:

                if st.button("Delete Task", key=f"delete_{task_id}"):

                    delete_task(task_id)

                    st.success("Task deleted!")

                    st.rerun()

else:

    st.info("No tasks found. Create your first task!")


st.divider()

st.subheader("🤖 Ask AI About Your Tasks")

question = st.text_input(
    "Ask a question about your task database",
    placeholder="How many tasks are completed?",
)

if st.button("Ask AI") and question:

    try:

        agent = initialize_agent()

        with st.spinner("AI is analyzing your database..."):

            response = agent.invoke({"input": question})

        st.success("AI Response")

        st.write(response["output"])

    except Exception as e:

        st.error(f"Error: {e}")
