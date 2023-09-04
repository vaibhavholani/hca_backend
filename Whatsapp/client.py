from dotenv import load_dotenv
import os
import messagebird

client = messagebird.Client(os.getenv("ACCESS_KEY"))
