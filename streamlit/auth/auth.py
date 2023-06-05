import os
import sys
sys.path.append(os.path.abspath('.'))
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def authenticate():
    with open('streamlit/auth/config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    for key, value in config['credentials']["usernames"].items():
        value['password'] = stauth.Hasher([value['password']]).generate()[0]

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    return authenticator