import os
from dotenv import load_dotenv

load_dotenv()

SOURCE_FILEPATH=os.getenv('SOURCE_FILEPATH')
DESTINATION_FILEPATH=os.getenv('DESTINATION_FILEPATH')