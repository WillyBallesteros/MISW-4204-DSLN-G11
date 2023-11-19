import os
from dotenv import load_dotenv

load_dotenv()

TASKS_TOPIC = os.getenv('TASKS_TOPIC')
EVENTS_TOPIC = os.getenv('EVENTS_TOPIC')
TMP_PATH = os.getenv('TMP_PATH')
PROCESS_ID = os.getpid()
PROJECT_ID = os.getenv('PROJECT_ID')