"""Python file to serve as the frontend"""
import os
import sys
from auth.auth import authenticate
sys.path.append(os.path.abspath('.'))
import streamlit as st
from streamlit_chat import message
from chain import load_chain
import traceback
from config import get_settings

settings = get_settings()


def submit():
    st.session_state.query = st.session_state.input
    st.session_state.input = ''

def get_text():
    """Logic for getting the text from the user should go here."""
    # input_text should be '' after hitting enter, we store the true input in query
    input_text = st.text_input("You: ", placeholder="ask me questions", key="input", on_change=submit)
    return st.session_state.query

def set_open_api_key(api_key: str):
        if api_key is None or api_key == '':
            st.session_state["open_api_key_configured"] = False
            print('OPENAI API key is NOT Configured Successfully!')
            st.stop()
        else:
            st.session_state["OPENAI_API_KEY"] = api_key
            st.session_state["open_api_key_configured"] = True
            print(st.session_state["open_api_key_configured"])
            print('OPENAI API key is Configured Successfully!')
        
def app():
    # Main app function
    st.header("📖 Vectorworks Documentation Chatbot Demo")
    st.write("My knowledge is based on the [documentation](https://app-help.vectorworks.net/2023/eng/index.htm) of Vectorworks.\
             Ask me questions about the documentation and I will try to answer them! 😎")
    st.markdown("""
                > For examples:
                >> - *How many modes are there for the rotate tool in the Vectorworks? What are they?*

                > Then you can verify the bot's answers in the related [documentation](https://app-help.vectorworks.net/2023/eng/VW2023_Guide/Objects_edit1/Rotate_tool.htm).
                > You can ask some follow-up questions, since the bot has memory up to 5 chats:

                >> - *Thanks! I would like to know more about the the alignment rotation mode. Can you show me how to use it?*

                > You can also ask the native ChatGPT same questions to compare the results.
                > We welcome your feedback! Reach me out through changyu.du@tum.de
                """)
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
        st.stop()


    else:
        st.markdown("Open API Key Configured!")
        chain = load_chain(st.session_state.get("OPENAI_API_KEY"))

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
                try:
                    output = chain({"question": user_input, "chat_history": st.session_state["chat_history"]})
                except Exception as e:
                    st.error(f"Error: {traceback.format_exc()}")
                    # clean up the query
                    st.session_state.query = ''
                    st.stop()
                st.session_state["chat_history"].append((user_input, output["answer"]))
                # only keep the last 5 history
                if len(st.session_state["chat_history"]) > 5:
                    st.session_state["chat_history"].pop(0)

                st.session_state.past.append(user_input)
                st.session_state.generated.append(output["answer"])
                # clean up the query
                st.session_state.query = ''

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
    
    # app without authentication
    if not settings.auth:
         # Main app function
        st.header("📖 Vectorworks Documentation Chatbot Demo")
        st.write("My knowledge is based on the [documentation](https://app-help.vectorworks.net/2023/eng/index.htm) of Vectorworks.\
                Ask me questions about the documentation and I will try to answer them! 😎")
        st.markdown("""
                    > For examples:
                    >> - *How many modes are there for the rotate tool in the Vectorworks? What are they?*

                    > Then you can verify the bot's answers in the related [documentation](https://app-help.vectorworks.net/2023/eng/VW2023_Guide/Objects_edit1/Rotate_tool.htm).
                    > You can ask some follow-up questions, since the bot has memory up to 5 chats:

                    >> - *Thanks! I would like to know more about the the alignment rotation mode. Can you show me how to use it?*

                    > You can also ask the native ChatGPT same questions to compare the results.
                    > We welcome your feedback! Reach me out through changyu.du@tum.de
                    """)
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
            st.stop()


        else:
            st.markdown("Open API Key Configured!")
            chain = load_chain(st.session_state.get("OPENAI_API_KEY"))

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
                    try:
                        output = chain({"question": user_input, "chat_history": st.session_state["chat_history"]})
                    except Exception as e:
                        st.error(f"Error: {traceback.format_exc()}")
                        # clean up the query
                        st.session_state.query = ''
                        st.stop()
                    st.session_state["chat_history"].append((user_input, output["answer"]))
                    # only keep the last 5 history
                    if len(st.session_state["chat_history"]) > 5:
                        st.session_state["chat_history"].pop(0)

                    st.session_state.past.append(user_input)
                    st.session_state.generated.append(output["answer"])
                    # clean up the query
                    st.session_state.query = ''

            if st.session_state["generated"]:

                for i in range(len(st.session_state["generated"]) - 1, -1, -1):
                    message(st.session_state["generated"][i], key=str(i))
                    message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")

    else:
        # authentication
        authenticator = authenticate()
        name, authentication_status, username = authenticator.login('Login', 'main')
        
        # when login
        if authentication_status:
            authenticator.logout('Logout', 'main', key='unique_key')
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
            st.session_state['OPEN_API_KEY'] = ""
            st.warning('Please enter your username and password')
            st.stop()

    