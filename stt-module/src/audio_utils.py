import ffmpeg
import os
import logging
from minio import Minio
from .config import (
    FFMPEG_PATH,
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_PORT
)
from .const import BLUE, RESET

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

minio_client = Minio(
    endpoint=f"{MINIO_ENDPOINT}:{MINIO_PORT}",
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

def convert_ts_to_wav(video_path: str, output_wav_path: str):
    """
    Converts a .ts video file from MinIO to WAV format using FFmpeg.
    Downloads from MinIO first, then converts.
    """

    output_dir = os.path.dirname(output_wav_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    bucket, object_name = video_path.split('/', 1)
    local_video_path = os.path.join(output_dir, os.path.basename(object_name))

    try:
        minio_client.fget_object(bucket, object_name, local_video_path)
        logging.info(f"{BLUE}[MINIO]{RESET} Downloaded {object_name} to {local_video_path}")
    except Exception as e:
        logging.error(f"{BLUE}[MINIO]{RESET} Failed to download '{object_name}' from bucket '{bucket}': {e}")
        raise

    try:
        (
            ffmpeg
            .input(local_video_path)
            .output(output_wav_path, acodec='pcm_s16le', ac=1, ar='16000')
            .run(cmd=FFMPEG_PATH, capture_stdout=True, capture_stderr=True)
        )
        logging.info(f"{BLUE}[AUDIO_UTILS]{RESET} Conversion successful. WAV saved to '{output_wav_path}'")
    except ffmpeg.Error as e:
        logging.error(f"{BLUE}[AUDIO_UTILS]{RESET} FFmpeg conversion failed for '{video_path}':")
        logging.error("Stderr: " + e.stderr.decode())
        logging.error("Stdout: " + e.stdout.decode())
        raise Exception(f"FFmpeg conversion failed: {e.stderr.decode()}")
    finally:
        if os.path.exists(local_video_path):
            os.remove(local_video_path)
