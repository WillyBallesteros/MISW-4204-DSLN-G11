import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL=os.getenv('DATABASE_URL')
PROJECT_ID = os.getenv('PROJECT_ID')
TASKS_TOPIC = os.getenv('TASKS_TOPIC')
EVENTS_TOPIC = os.getenv('EVENTS_TOPIC')
JWT_SECRET = os.getenv('JWT_SECRET')
SOURCE_FILEPATH=os.getenv('SOURCE_FILEPATH')
DESTINATION_FILEPATH=os.getenv('DESTINATION_FILEPATH')
PROCESS_ID = os.getpid()
