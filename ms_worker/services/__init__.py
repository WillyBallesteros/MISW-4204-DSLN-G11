import os
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
TASKS_QUEUE = os.getenv('TASKS_QUEUE')
EVENTS_QUEUE = os.getenv('EVENTS_QUEUE')
PROCESS_ID = os.getpid()