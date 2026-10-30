
import uuid

import streamlit as st
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import Tool
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

st.set_page_config(
    page_title="Google Search Agent",
    page_icon="🔎",
    layout="wide"
)

st.title("🔎 Google Search Agent")
st.caption("AI-powered web search using Google Serper and Groq")

@st.cache_resource
def initialize_agent():

    model = ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0,
        streaming=True
    )

    search = GoogleSerperAPIWrapper()

    search_tool = Tool(
        name="web_search",
        description=(
            "Search Google for relevant information. "
            "Use this tool whenever the user asks for "
            "current information or web research."
        ),
        func=search.run
    )

    memory = InMemorySaver()

    agent = create_agent(
        model=model,
        tools=[search_tool],
        checkpointer=memory,
        system_prompt=(
            "You are a helpful Google Search AI assistant. "
            "You can search the web for relevant information. "
            "Provide accurate, clear, and structured answers. "
            "Use previous messages in the current conversation "
            "when relevant. Do not invent search results."
        )
    )

    return agent


agent = initialize_agent()


if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())


config = {
    "configurable": {
        "thread_id": st.session_state.thread_id
    }
}

with st.sidebar:

    st.header("⚙️ Settings")

    st.success("Agent is ready")

    st.write("**LLM:** GPT-OSS-20B")
    st.write("**Search:** Google Serper")
    st.write("**Memory:** InMemorySaver")
    st.write("**Response:** Streaming")

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):

        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())

        st.rerun()

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


user_input = st.chat_input(
    "Ask me anything or search the web..."
)

if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):

        try:

            response_placeholder = st.empty()

            assistant_response = ""

            for token, metadata in agent.stream(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": user_input
                        }
                    ]
                },
                config=config,
                stream_mode="messages"
            ):

                if metadata.get("langgraph_node") != "model":
                    continue

                if isinstance(token.content, str):

                    if token.content:

                        assistant_response += token.content

                        response_placeholder.markdown(
                            assistant_response + "▌"
                        )

                elif isinstance(token.content, list):

                    for block in token.content:

                        if (
                            isinstance(block, dict)
                            and block.get("type") == "text"
                        ):

                            text_chunk = block.get("text", "")

                            assistant_response += text_chunk

                            response_placeholder.markdown(
                                assistant_response + "▌"
                            )

            response_placeholder.markdown(
                assistant_response
            )

            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_response
            })

        except Exception as e:

            st.error(f"Error: {e!s}")
