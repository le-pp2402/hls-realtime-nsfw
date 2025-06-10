import os
import logging
from .audio_utils import convert_ts_to_wav
from .whisper_processor import WhisperProcessor
from .rabbitmq import RabbitMQConsumer
from .config import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD, RABBITMQ_QUEUE, FFMPEG_PATH, TEMP_DIR, OUTPUT_DIR
import glob 
import shutil 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_video_file(video_path: str, processor: WhisperProcessor, output_base_name: str):
    """
    Processes a single video file: converts to WAV, transcribes, and saves output.

    Args:
        video_path: Path to the input video file.
        processor: An instance of WhisperProcessor with the loaded model.
        output_base_name: Base name for the output files (e.g., video1).
    """
    logging.info(f"Processing video: {video_path}")

    # --- Stage 1: Video to WAV Conversion ---
    # Create a temporary path for the WAV file
    os.makedirs(TEMP_DIR, exist_ok=True) 
    temp_wav_path = os.path.join(TEMP_DIR, f"{output_base_name}.wav")

    try:
        convert_video_to_wav(video_path, temp_wav_path)
    except Exception as e:
        logging.error(f"Skipping transcription due to FFmpeg error for {video_path}: {e}")
        if os.path.exists(temp_wav_path):
             os.remove(temp_wav_path)
        return 

    try:
        # Transcribe using the SAME processor instance
        segments, info = processor.transcribe_audio(temp_wav_path)

        # Process the segments and prepare output
        logging.info("Transcription segments:")
        for segment in segments:
            line = f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}"
            logging.info(line)
            transcription_output.append(line)

        # Optional: Save raw text or structured output (e.g., JSON)
        raw_text = "".join([segment.text for segment in segments])
        output_raw_text_path = os.path.join(OUTPUT_DIR, f"{output_base_name}_raw.txt")
        with open(output_raw_text_path, 'w', encoding='utf-8') as f:
            f.write(raw_text)
        logging.info(f"Raw transcription saved to {output_raw_text_path}")

        # Save the segment-by-segment output
        with open(output_text_path, 'w', encoding='utf-8') as f:
             for line in transcription_output:
                 f.write(line + '\n')
        logging.info(f"Segment transcription saved to {output_text_path}")

        # You could also pass 'segments' or 'raw_text' to another module here
        # another_module.process_transcription(output_base_name, segments, raw_text)

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
        callback_func=lambda ch, method, properties, body: process_message(body, whisper_processor)
    )
    
if __name__ == "__main__":
    main()