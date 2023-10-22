import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL=os.getenv('DATABASE_URL')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
TASKS_QUEUE = os.getenv('TASKS_QUEUE')
EVENTS_QUEUE = os.getenv('EVENTS_QUEUE')
JWT_SECRET = os.getenv('JWT_SECRET')
SOURCE_FILEPATH=os.getenv('SOURCE_FILEPATH')
DESTINATION_FILEPATH=os.getenv('DESTINATION_FILEPATH')
PROCESS_ID = os.getpid()
