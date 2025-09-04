import os
import time
import base64
import yaml
import logging
import asyncio
import requests
import aiohttp
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Optional, Any

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def load_config(file_path: str = "config.yaml") -> Dict[str, Any]:
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

config = load_config()

def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        logger.info("Function '%s' executed in %.4f seconds", func.__name__, duration)
        return result
    return wrapper


# ---------------------------
# Commands -/pull, /help, /introduce
# ---------------------------
def command(user_input: str) -> str:
    parts = user_input.strip().split(" ", 1)
    cmd, arg = parts[0], parts[1] if len(parts) > 1 else None

    if cmd == "/pull" and arg:
        return pull_model_in_background(arg)
    elif cmd == "/help":
        return "Commands:\n- /pull <model_name>\n- /introduce"
    elif cmd == "/introduce":
        audio_file_path = os.path.join("assets", "audios", "intro.mp3")
        if os.path.exists(audio_file_path):
            st.audio(audio_file_path, format="audio/mp3")
            return "Here’s my Introduction for you! 😎"
        else:
            return "Intro audio file not found."
    else:
        return "Invalid command. Use:\n- /help\n- /pull <model_name>\n- /introduce"


# ---------------------------
# Ollama Model Handling synchronously
# ---------------------------
def pull_ollama_model(model_name: str) -> Dict[str, Any]:
    url = f"{config['ollama']['base_url']}/api/pull"
    response = requests.post(url, json={"model": model_name})
    if response.status_code != 200:
        logger.error("Failed to pull %s: %s", model_name, response.text)
        return {"error": response.text}

    data = response.json()
    if "error" in data:
        return data["error"]["message"]

    st.session_state.model_options = list_ollama_models()
    st.success(f"Pulling {model_name} finished.")
    return data

# ---------------------------
# Ollama Model Handling asynchronously with retries
# ---------------------------
async def pull_ollama_model_async(model_name: str, stream: bool = True, retries: int = 1) -> str:
    url = f"{config['ollama']['base_url']}/api/pull"
    payload = {"model": model_name, "stream": stream}

    for attempt in range(1, retries + 1):
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=1800)) as session:
                async with session.post(url, json=payload) as response:
                    if stream:
                        async for chunk in response.content.iter_chunked(1024):
                            if chunk:
                                logger.debug("Received chunk: %s", chunk.decode(errors="ignore"))
                                st.info(chunk.decode("utf-8"))
                    else:
                        data = await response.json()
                        if "error" in data:
                            return data["error"]
                        st.session_state.model_options = list_ollama_models()
                        return f"Pull of {model_name} finished."
                    return "Pulled successfully"
        except asyncio.TimeoutError:
            logger.warning("Timeout on attempt %d", attempt)
        except Exception as e:
            logger.exception("Error pulling model: %s", str(e))
            break
    return f"Failed to pull {model_name} after {retries} attempts."


def pull_model_in_background(model_name: str, stream: bool = False):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        return asyncio.create_task(pull_ollama_model_async(model_name, stream=stream))
    return asyncio.run(pull_ollama_model_async(model_name, stream=stream))


# ---------------------------
# Model Listing
# ---------------------------
def list_openai_models() -> List[str]:
    api_key = os.getenv("OPENAI_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get("https://api.openai.com/v1/models", headers=headers)

    if response.status_code != 200:
        st.warning("OpenAI error: " + response.text)
        return []

    return [m["id"] for m in response.json().get("data", [])]


def list_ollama_models() -> List[str]:
    url = f"{config['ollama']['base_url']}/api/tags"
    response = requests.get(url).json()
    if response.get("error"):
        return []
    return [m["name"] for m in response.get("models", []) if "embed" not in m["name"]]


# ---------------------------
# Utility Helpers
# ---------------------------
def convert_bytes_to_base64(image_bytes: bytes, with_prefix: bool = False) -> str:
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}" if with_prefix else b64


def convert_ns_to_seconds(ns_value: int) -> float:
    return ns_value / 1_000_000_000

def get_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_avatar(sender_type: str) -> str:
    return os.path.join("assets", "icons", "UserImage.png" if sender_type == "user" else "BotImage.png")
