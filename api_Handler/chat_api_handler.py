import logging
import os
import requests
import streamlit as st
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv

from utils import (
    convert_bytes_to_base64,
    convert_bytes_to_base64_with_prefix,
    convert_ns_to_seconds,
    load_config,
)
from vectordb_handler import load_vectordb

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()
config = load_config()
openai_api_key = os.getenv("OPENAI_API_KEY")


class BaseChatAPIHandler:
    DEFAULT_TIMEOUT = 60  # seconds

    @classmethod
    def _post(cls, url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=cls.DEFAULT_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error("HTTP request failed: %s", e)
            raise
        except ValueError:
            logger.error("Invalid JSON response from %s", url)
            raise


class OpenAIChatAPIHandler(BaseChatAPIHandler):
    """Handler for OpenAI chat API."""
    API_URL = "https://api.openai.com/v1/chat/completions"

    @classmethod
    def api_call(cls, chat_history: List[Dict[str, Any]]) -> str:
        payload = {
            "model": st.session_state["model_to_use"],
            "messages": chat_history,
            "stream": False,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}",
        }

        data = cls._post(cls.API_URL, headers, payload)
        if "error" in data:
            return data["error"].get("message", "Unknown error from OpenAI")
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")

    @classmethod
    def image_chat(cls, user_input: str, chat_history: List[Dict[str, Any]], image: bytes) -> str:
        chat_history.append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_input},
                    {"type": "image_url", "image_url": {"url": convert_bytes_to_base64_with_prefix(image)}},
                ],
            }
        )
        return cls.api_call(chat_history)


class OllamaChatAPIHandler(BaseChatAPIHandler):
    """Handler for Ollama chat API."""

    @classmethod
    def api_call(cls, chat_history: List[Dict[str, Any]]) -> str:
        payload = {
            "model": st.session_state["model_to_use"],
            "messages": chat_history,
            "stream": False,
        }
        url = f"{config['ollama']['base_url'].rstrip('/')}/api/chat"

        data = cls._post(url, {"Content-Type": "application/json"}, payload)

        if "error" in data:
            return f"OLLAMA ERROR: {data['error']}"

        cls._print_times(data)
        return data.get("message", {}).get("content", "")

    @classmethod
    def image_chat(cls, user_input: str, chat_history: List[Dict[str, Any]], image: bytes) -> str:
        chat_history.append(
            {"role": "user", "content": user_input, "images": [convert_bytes_to_base64(image)]}
        )
        return cls.api_call(chat_history)

    @classmethod
    def _print_times(cls, data: Dict[str, Any]) -> None:
        times = {
            "Total duration": convert_ns_to_seconds(data.get("total_duration", 0)),
            "Load duration": convert_ns_to_seconds(data.get("load_duration", 0)),
            "Prompt eval duration": convert_ns_to_seconds(data.get("prompt_eval_duration", 0)),
            "Eval duration": convert_ns_to_seconds(data.get("eval_duration", 0)),
        }
        for k, v in times.items():
            logger.info("%s: %.4f seconds", k, v)


class ChatAPIHandler:
    """Unified handler that dispatches to OpenAI or Ollama."""

    @classmethod
    def chat(
        cls,
        user_input: str,
        chat_history: List[Dict[str, Any]],
        image: Optional[bytes] = None,
    ) -> str:
        endpoint = st.session_state.get("endpoint_to_use")
        model = st.session_state.get("model_to_use")
        logger.info("Using endpoint=%s, model=%s", endpoint, model)

        if endpoint == "openai":
            handler = OpenAIChatAPIHandler
        elif endpoint == "ollama":
            handler = OllamaChatAPIHandler
        else:
            raise ValueError(f"Unknown endpoint: {endpoint}")

        # PDF chat mode (RAG)
        if st.session_state.get("pdf_chat", False):
            vector_db = load_vectordb()
            retrieved = vector_db.similarity_search(
                user_input, k=config["chat_config"]["number_of_retrieved_documents"]
            )
            context = "\n".join([doc.page_content for doc in retrieved])
            template = f"Answer the user question based on this context:\n{context}\n\nUser Question: {user_input}"
            chat_history.append({"role": "user", "content": template})
            return handler.api_call(chat_history)

        # Image chat mode
        if image:
            return handler.image_chat(user_input, chat_history, image)

        # Default chat
        chat_history.append({"role": "user", "content": user_input})
        return handler.api_call(chat_history)
