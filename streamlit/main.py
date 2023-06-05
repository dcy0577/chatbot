"""Python file to serve as the frontend"""
import sys
import os
import dotenv
from langchain import LLMChain, PromptTemplate
import openai
from auth.auth import authenticate

# sys.path.append(os.path.abspath('.'))

import streamlit as st
from streamlit_chat import message
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
    Given the following extracted parts of a markdown format documentation and a question, create a final answer with references ("SOURCES"). 
    ALWAYS return a "SOURCES" part in your answer.
    If you don't find the answer to the user's question with the contents provided to you, answer that you didn't find the answer in the contents and propose him to rephrase his query with more details.
    If you are asked to provide code example, please provide at least one code snippet according to the given document.
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
    chain = ConversationalRetrievalChain(retriever=db.as_retriever(search_kwargs={"k": 1}), 
                                        question_generator=question_generator, 
                                        combine_docs_chain=doc_chain, 
                                        verbose =True)
    return chain


def submit():
    st.session_state.query = st.session_state.input
    st.session_state.input = ''

def get_text():
    """Logic for getting the text from the user should go here."""
    # input_text should be '' after hitting enter, we store the true input in something
    input_text = st.text_input("You: ", placeholder="ask me questions", key="input", on_change=submit)
    return st.session_state.query

def set_open_api_key(api_key: str):
        if api_key is None or api_key == '':
            st.session_state["open_api_key_configured"] = False
            print('OPENAI API key is NOT Configured Successfully!')
        else:
            st.session_state["OPENAI_API_KEY"] = api_key
            st.session_state["open_api_key_configured"] = True
            print(st.session_state["open_api_key_configured"])
            print('OPENAI API key is Configured Successfully!')
        
def app():
    # Main app function
    st.header("📖 Vectorwokrs Documentation Chatbot Demo")

    open_api_key_input = st.text_input(
            "Openai API Key",
            type="password",
            placeholder="Paste your API key here (sk-...)",
            help="You can get your API key from https://platform.openai.com/account/api-keys.",  # noqa: E501
            value=st.session_state.get("OPEN_API_KEY", ""),
        )

    if open_api_key_input:
        print(f'Entered API is {open_api_key_input}')
        set_open_api_key(open_api_key_input)

    if not st.session_state.get("open_api_key_configured"):
        st.error("Please configure your Open API key!")


    else:
        st.markdown("Open API Key Configured!")
        chain = load_chain()

        if "generated" not in st.session_state:
            st.session_state["generated"] = []

        if "past" not in st.session_state:
            st.session_state["past"] = []

        if 'query' not in st.session_state:
            st.session_state.query = ''

        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

        user_input = get_text()
        
        if user_input:
            with st.spinner("generating..."):
                output = chain({"question": user_input, "chat_history": st.session_state["chat_history"]})
                st.session_state["chat_history"].append((user_input, output["answer"]))
                # only keep the last 5 history
                if len(st.session_state["chat_history"]) > 5:
                    st.session_state["chat_history"].pop(0)

                st.session_state.past.append(user_input)
                st.session_state.generated.append(output["answer"])

        if st.session_state["generated"]:

            for i in range(len(st.session_state["generated"]) - 1, -1, -1):
                message(st.session_state["generated"][i], key=str(i))
                message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")

if __name__ == "__main__":
    # must be called as first streamlit command
    st.set_page_config(
        page_title="Vectorwokrs Documentation Chatbot Demo",
        page_icon="📖",
        layout="wide",
        initial_sidebar_state="expanded", )
    
    # authentication
    authenticator = authenticate()
    name, authentication_status, username = authenticator.login('Login', 'main')
    
    # when login
    if authentication_status:
        authenticator.logout('Logout', 'main', key='unique_key')
        if not st.session_state['logout']:
            
            st.write(f'Welcome *{name}*')
            # your application
            app()

    elif authentication_status is False:
        st.error('Username/password is incorrect')
    elif authentication_status is None:
        # reset when logout
        st.session_state.query = ''
        st.session_state["open_api_key_configured"] = False
        st.session_state['logout'] = False
        st.warning('Please enter your username and password')

    