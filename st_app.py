import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from typing import cast
import asyncio

# Initialize session state for chat history and runnable on first load
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ChatMessageHistory()
if "runnable" not in st.session_state:
    # Set up model, prompt and runnable
    model = ChatOpenAI(streaming=True, model="o1-mini"
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You're an Indian astrologer who specialises in providing marriage counselling.
                Ask a few questions related to astrology from the user in order to provide specific advice.But ask one question at a time and dont overwhelm them with multiple questions at once.
                Be brief while providing answers unless a lenghty explanation is needed.
                After each answer, please ask the user if they have any further questions or need more advice to keep them engaged.""",
            ),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )
    runnable = prompt | model | StrOutputParser()
    with_message_history = RunnableWithMessageHistory(
        runnable,
        lambda: st.session_state.chat_history,
        input_messages_key="input",
        history_messages_key="history",
        history_factory_config=[]
    )
    st.session_state.runnable = with_message_history

# Async function to handle the user's message input
async def handle_message(input_message: str):
    if not input_message:
        return

    runnable = cast(Runnable, st.session_state.runnable)
    # Placeholder for message streaming
    msg = ""
    # Use asynchronous streaming
    async for chunk in runnable.astream({"input": input_message}):
        msg += chunk
        st.session_state.current_output = msg  # Update the output as it streams


# Layout for user input
st.title("Astrology Marriage Counselor")
user_input = st.text_input("Enter your message:")

# Button to send message
if st.button("Send") and user_input:
    # Run the async function inside the event loop
    asyncio.run(handle_message(user_input))

# Display the chat history
for message in st.session_state.chat_history.messages:
    role = message.type
    content = message.content
    with st.chat_message(role):
        st.write(content)

# Display any ongoing streamed message
if "current_output" in st.session_state:
    with st.chat_message("assistant"):
        st.write(st.session_state.current_output)
