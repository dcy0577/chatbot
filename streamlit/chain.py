import sys
import os
sys.path.append(os.path.abspath('.'))
from langchain import LLMChain, PromptTemplate
import streamlit as st
from langchain.chains import ConversationChain, ConversationalRetrievalChain
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chat_models import ChatOpenAI
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from ingest import persist_directory, embeddings
from langchain.vectorstores import Chroma


def load_chain():
    """Logic for loading the chain you want to use should go here."""
    # load vector db if it exists
    with os.scandir(persist_directory) as it:
        if any(it):
            db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        else:
            raise Exception("No vector db found. Please run ingest.py to create one.")

    tech_template = """
    You are a chatbot that answers questions about vectorworks.
    Given the following extracted contents of markdown format documentation and a question, create a final answer with references ("SOURCES"). 
    ALWAYS return a "SOURCES" part in your answer.
    If you don't find the answer to the user's question with the contents provided to you, answer that you didn't find the answer in the contents and propose him to rephrase his query with more details.
    If needed, provide your answer in bullet points.
    If asked an irrelevant question, you will gently guide the conversation back to the topic of the documentation of vectorworks.
    The content are given in markdown format. You should use markdown syntax to understand the content.

    Question: {question}
    =========
    {context}
    =========
    Answer: """
    NEW_PROMPT = PromptTemplate(
        template=tech_template, input_variables=["context", "question"]
    )

    chat = ChatOpenAI(openai_api_key=st.session_state.get("OPENAI_API_KEY"), temperature=0)

    question_generator = LLMChain(llm=chat, verbose=True, prompt=CONDENSE_QUESTION_PROMPT)
    doc_chain = load_qa_with_sources_chain(chat, chain_type="stuff", 
                                        verbose=True, 
                                        prompt=NEW_PROMPT,
                                        document_variable_name = "context")
    chain = ConversationalRetrievalChain(retriever=db.as_retriever(search_kwargs={"k": 2}), 
                                        question_generator=question_generator, 
                                        combine_docs_chain=doc_chain, 
                                        verbose =True)
    return chain