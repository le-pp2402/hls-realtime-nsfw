    from faster_whisper import WhisperModel
    import logging
    import os
    from .config import MODEL_SIZE, DEVICE, COMPUTE_TYPE # Import config

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    class WhisperProcessor:
        """
        Manages the Faster Whisper model instance and performs transcription.
        The model is loaded once when the object is instantiated.
        """
        def __init__(self):
            """
            Loads the Faster Whisper model into memory.
            This constructor is called only once when the WhisperProcessor object is created.
            """
            logging.info(f"Loading Faster Whisper model: {MODEL_SIZE} on device: {DEVICE} with compute type: {COMPUTE_TYPE}")
            try:
                self.model = WhisperModel(
                    model_size_or_path=MODEL_SIZE,
                    device=DEVICE,
                    compute_type=COMPUTE_TYPE,
                )
                logging.info("Faster Whisper model loaded successfully.")
            except Exception as e:
                logging.error(f"Failed to load Faster Whisper model: {e}")
                raise

        def transcribe_audio(self, audio_path: str, language=None, **kwargs):
            """
            Transcribes an audio file using the loaded Whisper model.

            Args:
                audio_path: Path to the input audio file (should be in a compatible format,
                            preferably 16kHz, 16-bit PCM WAV as produced by audio_utils).
                language: Optional. The language of the audio (e.g., "en", "fr", "vi").
                        If None, Whisper will try to detect the language.
                **kwargs: Additional arguments for the transcribe method
                        (e.g., beam_size, vad_filter, word_timestamps).

            Returns:
                A tuple: (segments, info)
                segments: an iterator yielding the transcribed segments
                info: a TranscriptionInfo object
            Raises:
                FileNotFoundError: If the input audio file does not exist.
                Exception: If transcription fails.
            """
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Input audio file not found: {audio_path}")

            logging.info(f"Starting transcription for '{audio_path}'...")
            try:
                segments, info = self.model.transcribe(
                    audio_path,
                    language=language,
                    **kwargs
                )
                logging.info(f"Transcription finished for '{audio_path}'. Detected language: {info.language}, Probability: {info.language_probability:.2f}")
                return segments, info
            except Exception as e:
                logging.error(f"Transcription failed for '{audio_path}': {e}")
                raise