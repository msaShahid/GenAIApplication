import os

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Gemini Chat Assistant",
    page_icon="🤖",
    layout="centered",
)

st.title("🤖 Gemini Chat Assistant")
st.caption("Powered by Google Gemini and LangChain")

# Check for the API key
if not os.getenv("GOOGLE_API_KEY") and not os.getenv("GEMINI_API_KEY"):
    st.error("Google API key not found. Add GOOGLE_API_KEY to your .env file.")
    st.stop()


@st.cache_resource
def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-3.1-flash-lite",
        temperature=0.7,
        max_retries=2,
        streaming=True,
    )


try:
    llm = get_llm()
except Exception as e:
    st.error(f"Could not initialize Gemini: {e}")
    st.stop()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Clear chat button
if st.button("🗑️ Clear chat"):
    st.session_state.messages = []
    st.rerun()

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
prompt = st.chat_input("Ask me anything...")

if prompt:
    # Display and save the user's message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Convert conversation history into LangChain messages
    history = []
    for message in st.session_state.messages:
        if message["role"] == "user":
            history.append(HumanMessage(content=message["content"]))
        else:
            history.append(AIMessage(content=message["content"]))

    # Stream the assistant's response
    with st.chat_message("assistant"):
        try:
            with st.spinner("Gemini is thinking..."):
                response_stream = llm.stream(history)

                answer = st.write_stream(
                    chunk.text for chunk in response_stream if chunk.text
                )

            # Save the complete response to chat history
            st.session_state.messages.append({"role": "assistant", "content": answer})

        except Exception as e:
            st.error(
                "Something went wrong while contacting Gemini. "
                "Check your API key, model availability, "
                "and internet connection."
            )
            st.caption(f"Error details: {e}")
