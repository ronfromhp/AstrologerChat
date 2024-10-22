from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
from typing import cast

import chainlit as cl


@cl.on_chat_start
async def on_chat_start():
    model = ChatOpenAI(streaming=True)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You're an Indian astrologer who specialises in providing marriage counselling.
                Ask a few questions related to astrology from the user in order to provide specific advice.But ask one question at a time.
                Be brief while providing answers and keep them within a sentence or paragraph unless a lenghty explanation is needed.
                After providing any answer or advice, please ask the user if they have any further questions or need more advice to keep them engaged.""",
            ),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("chat_history", ChatMessageHistory())
    with_message_history = RunnableWithMessageHistory(
        runnable,
        lambda : cl.user_session.get("chat_history"),
        input_messages_key="input",
        history_messages_key="history",
        history_factory_config=[]
    )
    cl.user_session.set("runnable", with_message_history)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cast(Runnable, cl.user_session.get("runnable"))  # type: Runnable

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"input": message.content},
        # config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()
