import ffmpeg
import os
import logging
from .config import FFMPEG_PATH 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def convert_ts_to_wav(video_path: str, output_wav_path: str):
    """
    Converts a video file to WAV format using FFmpeg.
    Args:
        video_path: Path to the input video file.
        output_wav_path: Path where the output WAV file will be saved.

    Raises:
        FileNotFoundError: If the input video file does not exist.
        Exception: If FFmpeg conversion fails.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Input video file not found: {video_path}")
        # Define color codes
        BLUE = '\033[94m'
        RESET = '\033[0m'

        logging.info(f"{BLUE}[CONVERT]{RESET} Converting '{video_path}' to WAV format...")

        # Ensure the output directory exists
        output_dir = os.path.dirname(output_wav_path)
        if output_dir and not os.path.exists(output_dir):
             os.makedirs(output_dir, exist_ok=True)

        try:
            # -acodec pcm_s16le: use PCM 16-bit little-endian signed integer audio codec (standard for WAV)
            # -ac 1: convert to mono channel
            # -ar 16000: resample to 16 kHz (Whisper's expected sample rate)
            (
                ffmpeg
                .input(video_path)
                .output(output_wav_path, acodec='pcm_s16le', ac=1, ar='16000')
                .run(cmd=FFMPEG_PATH, capture_stdout=True, capture_stderr=True) 
            )
            logging.info(f"{BLUE}[CONVERT]{RESET} Conversion successful. WAV saved to '{output_wav_path}'")
        except ffmpeg.Error as e:
            logging.error(f"{BLUE}[CONVERT]{RESET} FFmpeg conversion failed for '{video_path}':")
            logging.error("Stderr: " + e.stderr.decode())
            logging.error("Stdout: " + e.stdout.decode())
            raise Exception(f"FFmpeg conversion failed: {e.stderr.decode()}")
        except FileNotFoundError:
             logging.error(f"{BLUE}[CONVERT]{RESET} FFmpeg command not found. Make sure FFmpeg is installed and in your system's PATH or specified correctly in config.py.")
             raise FileNotFoundError("FFmpeg command not found.")
        except Exception as e:
             logging.error(f"{BLUE}[CONVERT]{RESET} An unexpected error occurred during FFmpeg conversion: {e}")
             raise
