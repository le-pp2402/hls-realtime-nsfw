import os
import logging
from .audio_utils import convert_ts_to_wav
from .whisper_processor import WhisperProcessor
from .rabbitmq_consummer import RabbitMQConsumer
from .rabbitmq_publisher import RabbitMQPublisher
from .config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD, RABBITMQ_QUEUE, FFMPEG_PATH, TEMP_DIR, OUTPUT_DIR, RABBITMQ_OUTPUT_QUEUE
import glob 
import shutil 
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


rabbitmq_publisher = RabbitMQPublisher(
    host=RABBITMQ_HOST,
    queue_name=RABBITMQ_OUTPUT_QUEUE,
    port=RABBITMQ_PORT,
    username=RABBITMQ_USER,
    password=RABBITMQ_PASSWORD
)
rabbitmq_publisher.connect()

def process_video_file(message: str, processor: WhisperProcessor):
    """
    Processes a single video file: converts to WAV, transcribes, and saves output.

    Args:
        video_path: Path to the input video file.
        processor: An instance of WhisperProcessor with the loaded model.
    """
    message = json.loads(message)  

    video_path = message['Key']

    if (video_path.endswith('.ts') == False):
        return

    logging.info(f"Starting transcription for {video_path}")

    # --- Stage 1: Video to WAV Conversion ---
    # Create a temporary path for the WAV file
    os.makedirs(TEMP_DIR, exist_ok=True)
    temp_wav_path = os.path.join(TEMP_DIR, f"{os.path.basename(video_path)}.wav")

    try:
        convert_ts_to_wav(video_path, temp_wav_path)
    except Exception as e:
        logging.error(f"Skipping transcription due to FFmpeg error for {video_path}: {e}")
        if os.path.exists(temp_wav_path):
             os.remove(temp_wav_path)
        return 


    logging.info(f"Converted {video_path} to WAV format at {temp_wav_path}")

    try:
        segments, info = processor.transcribe_audio(temp_wav_path)

        logging.info("Transcription segments:")
        for segment in segments:
            rabbitmq_publisher.publish(segment.text)

    except FileNotFoundError:
         logging.error(f"Temporary WAV file not found for transcription: {temp_wav_path}")
    except Exception as e:
        logging.error(f"Transcription failed for {temp_wav_path}: {e}")
    finally:
        # --- Clean up temporary WAV file ---
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
            logging.info(f"Cleaned up temporary file: {temp_wav_path}")


def main():
    """
    Orchestrate the video processing pipeline.
    Loads the Whisper model once and processes all files in the input directory.
    """
    logging.info("Starting video transcription project...")

    try:
        whisper_processor = WhisperProcessor()
    except Exception as e:
        logging.critical(f"Failed to initialize Whisper processor. Exiting. Error: {e}")
        return

    rabbitmq_client = RabbitMQConsumer(
        host=RABBITMQ_HOST,
        queue_name=RABBITMQ_QUEUE,
        port=RABBITMQ_PORT,
        username=RABBITMQ_USER,
        password=RABBITMQ_PASSWORD
    )
    rabbitmq_client.connect()
    logging.info("Connected to RabbitMQ. Waiting for messages...")

    rabbitmq_client.start_consuming(
        callback_func=lambda body: process_video_file(body, whisper_processor)
    )
    
if __name__ == "__main__":
    main()