import asyncio
import os
from typing import AsyncGenerator, AsyncIterable, Awaitable
from langchain import LLMChain

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from pydantic import BaseModel
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from prompt import NEW_PROMPT
from config import settings
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains import RetrievalQAWithSourcesChain, RetrievalQA, ConversationalRetrievalChain, LLMChain




async def generate_response(self, conversation_id: str, message: str
) -> AsyncGenerator[str, None]:

    callback_handler  = AsyncIteratorCallbackHandler()

    q_generator_llm = ChatOpenAI(
        openai_api_key=settings.openai_api_key,
    )

    streaming_llm = ChatOpenAI(
        openai_api_key=settings.openai_api_key,
        streaming=True,
        callbacks=[callback_handler],
    )

    question_generator = LLMChain(llm=q_generator_llm, prompt=CONDENSE_QUESTION_PROMPT)
    doc_chain = load_qa_with_sources_chain(llm=streaming_llm, chain_type="stuff", prompt=NEW_PROMPT)

    qa_chain = ConversationalRetrievalChain(
        retriever=collection_store.as_retriever(search_kwargs={"k": 3}),
        combine_docs_chain=doc_chain,
        question_generator=question_generator,
        return_source_documents=True,
    )

    history = []

    task = asyncio.create_task(
        qa_chain.acall({
            "question": q,
            "chat_history": history
        }),
    )

    history.append((question, result["answer"]))

    async for token in callback_handler.aiter():
        yield token

    await task