from dotenv import load_dotenv
from pathlib import Path
from src.utils.logger import create_logger
log = create_logger(__name__)

def load_env(env_file: str, fallover=True):
    if Path(env_file).is_file():
        log.info(f"Loading env variables from ENV_FILE: {env_file}")
        load_dotenv(env_file)
    #elif fallover and Path(".env").is_file():
    #    load_dotenv()
    else:

        log.info("No .env file found. Using environment variables.")
