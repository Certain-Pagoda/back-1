from dotenv import load_dotenv
from pathlib import Path

def load_env(env_file: str, fallover=True):
    if Path(env_file).is_file():
        load_dotenv(env_file)
    elif fallover and Path(".env").is_file():
        load_dotenv()
