import io
import logging
import subprocess
import tempfile
import librosa
from typing import Union
from functools import lru_cache
from transformers import pipeline
from utils import load_config, timeit

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

config = load_config()

def convert_webm_to_wav_ffmpeg(audio_bytes: bytes) -> io.BytesIO:
    """
    Convert WebM bytes to WAV (PCM 16-bit) using ffmpeg.
    Returns an in-memory BytesIO buffer.
    """
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f_in, \
         tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f_out:

        f_in.write(audio_bytes)
        f_in.flush()

        cmd = [
            "ffmpeg", "-y", "-fflags", "+igndts",
            "-i", f_in.name,
            "-c:a", "pcm_s16le",
            f_out.name
        ]
        result = subprocess.run(cmd, capture_output=True)

        if result.returncode != 0:
            logger.error("FFmpeg failed: %s", result.stderr.decode())
            raise RuntimeError("FFmpeg conversion failed")

        with open(f_out.name, "rb") as f:
            wav_bytes = f.read()

    return io.BytesIO(wav_bytes)


def convert_bytes_to_array(audio_bytes: bytes) -> tuple:
    """
    Convert audio bytes (WebM or WAV) to numpy array and sample rate.
    Falls back to ffmpeg conversion if needed.
    """
    try:
        audio_io = io.BytesIO(audio_bytes)
        audio, sr = librosa.load(audio_io, sr=None)
        return audio, sr
    except Exception as e:
        logger.warning("Direct load failed (%s), trying ffmpeg fallback.", e)
        wav_io = convert_webm_to_wav_ffmpeg(audio_bytes)
        audio, sr = librosa.load(wav_io, sr=None)
        return audio, sr


@lru_cache(maxsize=1)
def get_asr_pipeline(device: Union[int, str] = "cpu"):
    """
    Lazily load and cache the Whisper ASR pipeline.
    """
    model_name = config.get("whisper_model", "openai/whisper-small")
    logger.info("Loading ASR pipeline (model=%s, device=%s)", model_name, device)

    return pipeline(
        task="automatic-speech-recognition",
        model=model_name,
        chunk_length_s=30,
        device=device,
    )


@timeit
def transcribe_audio(audio_bytes: bytes, device: str = "cpu") -> str:
    try:
        audio_array, sr = convert_bytes_to_array(audio_bytes)
        logger.info("Audio loaded (sample_rate=%d, duration=%.2fs)", sr, len(audio_array) / sr)

        asr = get_asr_pipeline(device)
        prediction = asr(audio_array, batch_size=1)

        return prediction.get("text", "").strip()

    except Exception as e:
        logger.error("Transcription failed: %s", e)
        raise
