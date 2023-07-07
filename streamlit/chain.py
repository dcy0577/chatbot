import sys
import os
sys.path.append(os.path.abspath('.'))
from langchain import LLMChain, PromptTemplate
import streamlit as st
from langchain.chains import ConversationChain, ConversationalRetrievalChain
from langchain.chains.conversational_retrieval.prompts import CONDENSE_QUESTION_PROMPT
from langchain.chat_models import ChatOpenAI
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from ingest import persist_directory, load_embeddings
from langchain.vectorstores import Chroma

@st.cache_resource
def load_persist_db(persist_directory, _embeddings):
    with os.scandir(persist_directory) as it:
        if any(it):
            return Chroma(persist_directory=persist_directory, embedding_function=_embeddings)
        else:
            raise Exception("No vector db found. Please run ingest.py to create one.")

def load_chain(openai_api_key: str):
    """Logic for loading the chain you want to use should go here."""

    # initialize chat model
    chat = ChatOpenAI(model_name="gpt-4", openai_api_key=openai_api_key, temperature=0)

    # load embeddings
    embeddings = load_embeddings()

    # load vector db if it exists
    db = load_persist_db(persist_directory, embeddings)

    tech_template = """
    You are a helpful assistant that answers user's questions about vectorworks.
    Given the following extracted contents of markdown format documentation and a question, create a final answer with references ("SOURCES"). 
    If you don't find the answer to the user's question with the contents provided to you, answer that you didn't find the answer in the contents and propose him to rephrase his query with more details.
    If needed, provide your answer in bullet points.
    If asked an irrelevant question, you will gently guide the conversation back to the topic of the documentation of vectorworks.
    The extracted contents are given in markdown format. You should use markdown syntax to understand the content. You don't need to use markdown syntax to answer the user's question.

    Question: {question}
    =========
    {context}
    =========
    Answer: """
    NEW_PROMPT = PromptTemplate(
        template=tech_template, input_variables=["context", "question"]
    )

    question_generator = LLMChain(llm=chat, verbose=True, prompt=CONDENSE_QUESTION_PROMPT)
    doc_chain = load_qa_with_sources_chain(chat, chain_type="stuff", 
                                        verbose=True, 
                                        prompt=NEW_PROMPT,
                                        document_variable_name = "context")
    chain = ConversationalRetrievalChain(retriever=db.as_retriever(search_kwargs={"k": 2}), 
                                        question_generator=question_generator, 
                                        combine_docs_chain=doc_chain,
                                        max_tokens_limit=4096, 
                                        verbose =True)
    return chain