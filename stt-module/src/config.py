import os
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

#WHISPER MODEL CONFIGURATION
# Get model size from env var, default to 'large-v2'
MODEL_SIZE = os.getenv("MODEL_SIZE", "large-v2")
# Get device from env var, default to 'auto' (CPU or GPU if available)
DEVICE = os.getenv("DEVICE", "auto")
COMPUTE_TYPE = os.getenv("COMPUTE_TYPE", "int8") # Or 'float16', 'int8_float16'


#RABBITMQ CONFIGURATION
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))  
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "video_transcription")

#FFMPEG CONFIGURATION
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "/usr/bin/ffmpeg")

#DIRECTORIES
TEMP_DIR = os.getenv("TEMP_DIR", "temp")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")