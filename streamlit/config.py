import os
import sys
sys.path.append(os.path.abspath('.'))
from typing import Any, Dict, List, Optional
import functools
import dotenv
from pydantic import BaseSettings

dotenv.load_dotenv(dotenv_path='streamlit/deploy.env')


class Settings(BaseSettings):

    auth: Optional[bool]

@functools.lru_cache
def get_settings():
    return Settings()
