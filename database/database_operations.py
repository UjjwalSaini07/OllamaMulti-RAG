import logging
import sqlite3
import streamlit as st
from typing import Any, Dict, List, Optional, Tuple
from utils import load_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

config = load_config()
DB_PATH = config.get("chat_sessions_database_path", "chatSessionCache.db")

# ---------------------------
# Connection Management
# ---------------------------
def get_db_connection() -> sqlite3.Connection:
    """
    Return an existing Streamlit session DB connection or create a new one.
    """
    if "db_conn" not in st.session_state or st.session_state.db_conn is None:
        st.session_state.db_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return st.session_state.db_conn

def close_db_connection() -> None:
    conn: Optional[sqlite3.Connection] = st.session_state.get("db_conn")
    if conn:
        conn.close()
        st.session_state.db_conn = None
        logger.info("Database connection closed.")

# ---------------------------
# Schema Initialization
# ---------------------------
def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_history_id TEXT NOT NULL,
                sender_type TEXT NOT NULL,
                message_type TEXT NOT NULL,
                text_content TEXT,
                blob_content BLOB
            );
            """
        )
        conn.commit()
    logger.info("Database initialized at %s", DB_PATH)

# ---------------------------
# Insert Operations
# ---------------------------
def _insert_message(chat_history_id: str, sender_type: str, message_type: str, text: Optional[str] = None, blob: Optional[bytes] = None) -> None:
    """
    Insert a message (text/image/audio) into DB.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO messages (chat_history_id, sender_type, message_type, text_content, blob_content)
        VALUES (?, ?, ?, ?, ?)
        """,
        (chat_history_id, sender_type, message_type, text, sqlite3.Binary(blob) if blob else None),
    )
    conn.commit()
    logger.debug("Inserted %s message into chat %s", message_type, chat_history_id)


def save_text_message(chat_history_id: str, sender_type: str, text: str) -> None:
    _insert_message(chat_history_id, sender_type, "text", text=text)


def save_image_message(chat_history_id: str, sender_type: str, image_bytes: bytes) -> None:
    _insert_message(chat_history_id, sender_type, "image", blob=image_bytes)


def save_audio_message(chat_history_id: str, sender_type: str, audio_bytes: bytes) -> None:
    _insert_message(chat_history_id, sender_type, "audio", blob=audio_bytes)

# ---------------------------
# Retrieval Operations - Load all messages for a chat history.
# ---------------------------
def load_messages(chat_history_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT message_id, sender_type, message_type, text_content, blob_content FROM messages WHERE chat_history_id = ?",
        (chat_history_id,),
    )
    messages = cursor.fetchall()

    chat_history = []
    for message_id, sender_type, message_type, text_content, blob_content in messages:
        content = text_content if message_type == "text" else blob_content
        chat_history.append(
            {"message_id": message_id, "sender_type": sender_type, "message_type": message_type, "content": content}
        )
    return chat_history

def load_last_k_text_messages(chat_history_id: str, k: int) -> List[Dict[str, Any]]:
    """
    Load last K text messages (for context).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT message_id, sender_type, message_type, text_content
        FROM messages
        WHERE chat_history_id = ? AND message_type = 'text'
        ORDER BY message_id DESC
        LIMIT ?
        """,
        (chat_history_id, k),
    )
    messages = cursor.fetchall()

    return [
        {"message_id": mid, "sender_type": sender, "message_type": mtype, "content": text}
        for mid, sender, mtype, text in reversed(messages)
    ]

def load_last_k_text_messages_ollama(chat_history_id: str, k: int) -> List[Dict[str, Any]]:
    """
    Load last K text messages in Ollama-compatible format.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT message_id, sender_type, message_type, text_content
        FROM messages
        WHERE chat_history_id = ? AND message_type = 'text'
        ORDER BY message_id DESC
        LIMIT ?
        """,
        (chat_history_id, k),
    )
    messages = cursor.fetchall()

    return [{"role": sender, "content": text} for mid, sender, mtype, text in reversed(messages)]

def get_all_chat_history_ids() -> List[str]:
    """
    Retrieve distinct chat_history_id values.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT chat_history_id FROM messages ORDER BY chat_history_id ASC")
    return [row[0] for row in cursor.fetchall()]

# ---------------------------
# Delete Operations - Delete all messages belonging to a chat history.
# ---------------------------
def delete_chat_history(chat_history_id: str) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE chat_history_id = ?", (chat_history_id,))
    conn.commit()
    logger.warning("Deleted all messages for chat_history_id=%s", chat_history_id)

# ---------------------------
# Main Entrypoint
# ---------------------------
if __name__ == "__main__":
    init_db()
