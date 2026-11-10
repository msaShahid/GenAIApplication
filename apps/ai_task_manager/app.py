
import streamlit as st
from ai_agent import ask_ai
from config import PRIORITIES, TASK_STATUSES
from database import (
    add_task,
    delete_task,
    get_task_statistics,
    get_tasks,
    initialize_database,
    update_task,
)

st.set_page_config(
    page_title="AI Task Manager",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_database()

def show_error(error):

    st.error(str(error))


def render_task(task):

    with st.expander(
        f"#{task['id']} - {task['title']} | {task['status']}"
    ):

        st.write("**Description:**", task["description"] or "N/A")

        st.write("**Priority:**", task["priority"])

        st.write("**Created:**", task["created_at"])

        new_status = st.selectbox(
            "Task Status",
            TASK_STATUSES,
            index=TASK_STATUSES.index(task["status"]),
            key=f"status_{task['id']}",
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "Update Status",
                key=f"update_{task['id']}",
                use_container_width=True,
            ):

                try:

                    updated = update_task(
                        task["id"],
                        new_status,
                    )

                    if updated:
                        st.success("Task updated successfully!")
                    else:
                        st.warning("Task not found.")

                    st.rerun()

                except Exception as error:
                    show_error(error)

        with col2:

            if st.button(
                "Delete Task",
                key=f"delete_{task['id']}",
                use_container_width=True,
                type="secondary",
            ):

                try:

                    delete_task(task["id"])

                    st.success("Task deleted successfully!")

                    st.rerun()

                except Exception as error:
                    show_error(error)

st.title("📋 AI Database Task Manager")

st.caption(
    "Manage your tasks with SQLite, Streamlit and Groq AI."
)

st.divider()

st.sidebar.header("➕ Create New Task")

with st.sidebar.form("create_task_form", clear_on_submit=True):

    task_title = st.text_input(
        "Task Title",
        max_chars=200,
        placeholder="Enter task title...",
    )

    task_description = st.text_area(
        "Description",
        placeholder="Enter task description...",
    )

    task_priority = st.selectbox(
        "Priority",
        PRIORITIES,
        index=1,
    )

    submitted = st.form_submit_button(
        "Add Task",
        use_container_width=True,
    )

    if submitted:

        try:

            add_task(
                task_title,
                task_description,
                task_priority,
            )

            st.sidebar.success(
                "Task added successfully!"
            )

            st.rerun()

        except ValueError as error:
            st.sidebar.warning(str(error))

        except Exception as error:
            st.sidebar.error(
                f"Unable to create task: {error}"
            )


st.subheader("📊 Dashboard")

stats = get_task_statistics()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Tasks",
    stats["total"] or 0,
)

col2.metric(
    "Pending",
    stats["pending"] or 0,
)

col3.metric(
    "In Progress",
    stats["in_progress"] or 0,
)

col4.metric(
    "Completed",
    stats["completed"] or 0,
)


st.divider()

st.subheader("📌 All Tasks")

tasks = get_tasks()

filter_status = st.selectbox(
    "Filter Tasks",
    ["All"] + TASK_STATUSES,
)

if filter_status != "All":

    tasks = [
        task for task in tasks
        if task["status"] == filter_status
    ]


if tasks:

    for task in tasks:
        render_task(task)

else:

    st.info(
        "No tasks found. Create your first task!"
    )


st.divider()


st.subheader("🤖 Ask AI About Your Tasks")

st.caption(
    "Ask natural-language questions about your task database."
)

with st.form("ai_question_form"):

    question = st.text_input(
        "Your Question",
        placeholder="How many tasks are completed?",
        max_chars=1000,
    )

    ask_button = st.form_submit_button(
        "Ask AI",
        use_container_width=True,
    )


if ask_button:

    if not question.strip():

        st.warning("Please enter a question.")

    else:

        try:

            with st.spinner(
                "AI is analyzing your tasks..."
            ):

                answer = ask_ai(question)

            st.success("AI Response")

            st.markdown(answer)

        except ValueError as error:

            st.warning(str(error))

        except Exception:

            st.error(
                "Something went wrong while processing "
                "your question. Please try again."
            )

st.divider()

st.caption(
    "Built with Streamlit | SQLite | LangChain | Groq"
)
