import os
import sqlite3
import redis
from pathlib import Path
from PIL import Image
import streamlit as st
from streamlit_mic_recorder import mic_recorder
from chat_api_handler import ChatAPIHandler
from utils import (
    get_timestamp, load_config, get_avatar,
    list_openai_models, list_ollama_models, command
)
from utils.audio_handler import transcribe_audio
from utils.pdf_handler import add_documents_to_db
from utils.html_templates import css
from database_operations import (
    save_text_message, save_image_message, save_audio_message,
    load_messages, get_all_chat_history_ids,
    delete_chat_history, load_last_k_text_messages_ollama
)

# ==================================================================
#  Project   : Neura-Nix - Multimodal AI Assistant {Ollama MultiRag}
#  Author    : UjjwalS (https://www.ujjwalsaini.dev)
#  License   : Apache-2.0
#  Copyright : © 2025 UjjwalS. All rights reserved.
# ==================================================================
config = load_config()

# For Redis LocalHost
# redis_client = redis.Redis(
#     host=os.getenv("REDIS_HOST", "localhost"),
#     port=int(os.getenv("REDIS_PORT", 6379)),
#     db=0,
#     decode_responses=True
# )

# For Redis Cloud
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis-12345.c15.us-east-1-2.ec2.cloud.redislabs.com"),
    port=int(os.getenv("REDIS_PORT", 12345)),
    password=os.getenv("REDIS_PASSWORD"), 
    ssl=True,
    decode_responses=True
)

logo_long_image = Image.open("assets/logo_long_image.png")
logo_short_image = Image.open("assets/logo_short_image.png")

# ---------------------------
# Sidebar Footer
# ---------------------------
def sidebar_footer():
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 5px; text-align: center; font-size: 0.9em; color: #999;">
                Powered by Ollama & OpenAI
            </div>
            <div style="padding: 2px; text-align: center; font-size: 1em; color: #fff;">
                Built with dedication by <strong>UjjwalS</strong>
            </div>
            """,
            unsafe_allow_html=True
        )

# ---------------------------
# Session Helpers
# ---------------------------
def toggle_pdf_chat():
    st.session_state.pdf_chat = True
    clear_cache()


def detoggle_pdf_chat():
    st.session_state.pdf_chat = False


def get_session_key():
    if st.session_state.session_key == "new_session":
        st.session_state.new_session_key = get_timestamp()
        return st.session_state.new_session_key
    return st.session_state.session_key


def delete_chat_session_history():
    delete_chat_history(st.session_state.session_key)
    st.session_state.session_index_tracker = "new_session"

#  Author: UjjwalS (https://www.ujjwalsaini.dev)
def clear_cache():
    """Clear Redis cache."""
    redis_client.flushdb()


def list_model_options():
    endpoint = st.session_state.endpoint_to_use
    cache_key = f"models:{endpoint}"

    if redis_client.exists(cache_key):
        return redis_client.lrange(cache_key, 0, -1)

    if endpoint == "ollama":
        ollama_options = list_ollama_models()
        if not ollama_options:
            st.warning("No Ollama models found. Visit https://ollama.com/library and pull one with /pull <model_name>")
        if ollama_options:
            redis_client.rpush(cache_key, *ollama_options)
        return ollama_options

    elif endpoint == "openai":
        openai_options = list_openai_models()
        if openai_options:
            redis_client.rpush(cache_key, *openai_options)
        return openai_options


def update_model_options():
    st.session_state.model_options = list_model_options()

# ---------------------------
# Main Application
# ---------------------------
def main():
    st.set_page_config(
        page_title="Neura-Nix: Multimodal Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    #  Author: UjjwalS (https://www.ujjwalsaini.dev)
    st.write(css, unsafe_allow_html=True)

    st.title("Neura-Nix: Multimodal Assistant")

    st.markdown(
        """
        <div style="font-size: 1.05em; line-height: 1.6; padding: 8px; 
                    background-color: #2b313e; border-radius: 8px; color: #e6e6e6;">
            Neura-Nix is a **context-aware multimodal assistant** that enables seamless interaction 
            across text, images, PDFs, and audio.  
            Designed for clarity, efficiency, and adaptability — it transforms diverse inputs 
            into coherent, actionable insights.  
        </div>
        """,
        unsafe_allow_html=True
    )

    # Feature highlights
    st.markdown("### Capabilities")
    text_col, image_col, audio_col = st.columns(3)
    text_col.success("📑 Query and summarize PDFs")
    image_col.success("🖼️ Analyze and interpret images")
    audio_col.success("🎙️ Converse through audio inputs")

    # Session initialization
    if "db_conn" not in st.session_state:
        st.session_state.session_key = "new_session"
        st.session_state.new_session_key = None
        st.session_state.session_index_tracker = "new_session"
        st.session_state.db_conn = sqlite3.connect(config["chat_sessions_database_path"], check_same_thread=False)
        st.session_state.audio_uploader_key = 0
        st.session_state.pdf_uploader_key = 1
        st.session_state.endpoint_to_use = "ollama"
        st.session_state.model_options = list_model_options()
        st.session_state.model_tracker = None

    if st.session_state.session_key == "new_session" and st.session_state.new_session_key is not None:
        st.session_state.session_index_tracker = st.session_state.new_session_key
        st.session_state.new_session_key = None

    # Sidebar: Chat sessions
    st.sidebar.title("Chat History")
    chat_sessions = ["new_session"] + get_all_chat_history_ids()

    try:
        index = chat_sessions.index(st.session_state.session_index_tracker)
    except ValueError:
        st.session_state.session_index_tracker = "new_session"
        index = 0
        clear_cache()

    st.sidebar.selectbox("Select a chat session", chat_sessions, key="session_key", index=index)
    st.sidebar.button("Delete Chat Session", on_click=delete_chat_session_history)

    # Sidebar: API settings
    api_col, model_col = st.sidebar.columns(2)
    api_col.selectbox("Provider", ["ollama", "openai"], key="endpoint_to_use", on_change=update_model_options)
    model_col.selectbox("Model", st.session_state.model_options, key="model_to_use")

    pdf_toggle_col, voice_rec_col = st.sidebar.columns(2)
    pdf_toggle_col.toggle("Enable PDF Chat", key="pdf_chat", value=False, on_change=clear_cache)

    with voice_rec_col:
        voice_recording = mic_recorder(start_prompt="🎤 Start", stop_prompt="⏹ Stop", just_once=True)

    # File uploaders
    st.sidebar.title("Input Options")
    with st.sidebar.expander("Upload Files", expanded=False):
        uploaded_pdf = st.file_uploader("PDF", accept_multiple_files=True, key=st.session_state.pdf_uploader_key, type=["pdf"], on_change=toggle_pdf_chat)
        uploaded_image = st.file_uploader("Image", type=["jpg", "jpeg", "png"], on_change=detoggle_pdf_chat)
        uploaded_audio = st.file_uploader("Audio", type=["wav", "mp3", "ogg"], key=st.session_state.audio_uploader_key)

    sidebar_footer()

    # Chat container
    chat_container = st.container()
    user_input = st.chat_input("Enter your query here...")

    # ---------------------------
    # Process Uploaded Files
    # ---------------------------
    if uploaded_pdf:
        with st.spinner("Processing PDF..."):
            add_documents_to_db(uploaded_pdf)
            st.session_state.pdf_uploader_key += 2

    if voice_recording:
        transcribed_audio = transcribe_audio(voice_recording["bytes"])
        llm_answer = ChatAPIHandler.chat(
            user_input=transcribed_audio,
            chat_history=load_last_k_text_messages_ollama(get_session_key(), config["chat_config"]["chat_memory_length"])
        )
        save_audio_message(get_session_key(), "user", voice_recording["bytes"])
        save_text_message(get_session_key(), "assistant", llm_answer)

    if user_input:
        if user_input.startswith("/"):
            response = command(user_input)
            save_text_message(get_session_key(), "user", user_input)
            save_text_message(get_session_key(), "assistant", response)
            user_input = None

        elif uploaded_image:
            with st.spinner("Processing image..."):
                llm_answer = ChatAPIHandler.chat(
                    user_input=user_input,
                    chat_history=[],
                    image=uploaded_image.getvalue()
                )
                save_text_message(get_session_key(), "user", user_input)
                save_image_message(get_session_key(), "user", uploaded_image.getvalue())
                save_text_message(get_session_key(), "assistant", llm_answer)
                user_input = None

        elif uploaded_audio:
            transcribed_audio = transcribe_audio(uploaded_audio.getvalue())
            llm_answer = ChatAPIHandler.chat(
                user_input=user_input + "\n" + transcribed_audio,
                chat_history=[]
            )
            save_text_message(get_session_key(), "user", user_input)
            save_audio_message(get_session_key(), "user", uploaded_audio.getvalue())
            save_text_message(get_session_key(), "assistant", llm_answer)
            st.session_state.audio_uploader_key += 2
            user_input = None

        elif user_input:
            llm_answer = ChatAPIHandler.chat(
                user_input=user_input,
                chat_history=load_last_k_text_messages_ollama(get_session_key(), config["chat_config"]["chat_memory_length"])
            )
            save_text_message(get_session_key(), "user", user_input)
            save_text_message(get_session_key(), "assistant", llm_answer)
            user_input = None

    # ---------------------------
    # Display Chat History
    # ---------------------------
    if (st.session_state.session_key != "new_session") != (st.session_state.new_session_key is not None):
        with chat_container:
            chat_history_messages = load_messages(get_session_key())
            for message in chat_history_messages:
                with st.chat_message(name=message["sender_type"], avatar=get_avatar(message["sender_type"])):
                    if message["message_type"] == "text":
                        st.write(message["content"])
                    elif message["message_type"] == "image":
                        st.image(message["content"])
                    elif message["message_type"] == "audio":
                        st.audio(message["content"], format="audio/wav")

        if st.session_state.session_key == "new_session" and st.session_state.new_session_key is not None:
            st.rerun()

#  Author: UjjwalS (https://www.ujjwalsaini.dev)
if __name__ == "__main__":
    main()
