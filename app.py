from dotenv import load_dotenv
import os

load_dotenv()  # This will load variables from .env file

# Now you can use PROJ_DIR from environment variables
proj_dir = os.getenv('PROJ_DIR')
print(f"PROJ_DIR is set to: {proj_dir}")

