# 🤖 OllamaMulti-RAG: Neura-Nix
> **An AI-powered multimodal assistant that seamlessly understands Text, Images, PDFs, and Audio — built to boost productivity, empower businesses, and transform everyday workflows.**  

<!--<img src="./assets/Logo.png" alt="Neura-Nix Logo" width="150"/>-->

## 🌟 Introduction
**Neura-Nix** is a next-gen **multimodal assistant** that combines the power of **Ollama, OpenAI, Whisper, and Redis** into a single streamlined platform.  
It enables natural and intelligent interaction across different mediums — **chat with documents, analyze images, transcribe audio, and converse in real-time**.  

Built with **Streamlit**, **Docker**, and **Redis caching**, Neura-Nix is designed for **speed, extensibility, and scalability**.  
Whether you’re an **enterprise optimizing workflows** or an **individual boosting productivity**, Neura-Nix adapts seamlessly.  

[![Github License](https://img.shields.io/github/license/UjjwalSaini07/OllamaMulti-RAG)](https://github.com/UjjwalSaini07/OllamaMulti-RAG/blob/main/LICENSE)
[![Info](https://img.shields.io/badge/Project-Info-blue?style=flat&logo=data:image/svg%2bxml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iaXNvLTg4NTktMSI/Pg0KPCEtLSBHZW5lcmF0b3I6IEFkb2JlIElsbHVzdHJhdG9yIDE5LjAuMCwgU1ZHIEV4cG9ydCBQbHVnLUluIC4gU1ZHIFZlcnNpb246IDYuMDAgQnVpbGQgMCkgIC0tPg0KPHN2ZyB2ZXJzaW9uPSIxLjEiIGlkPSJDYXBhXzEiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6eGxpbms9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkveGxpbmsiIHg9IjBweCIgeT0iMHB4Ig0KCSB2aWV3Qm94PSIwIDAgNTEyIDUxMiIgc3R5bGU9ImVuYWJsZS1iYWNrZ3JvdW5kOm5ldyAwIDAgNTEyIDUxMjsiIHhtbDpzcGFjZT0icHJlc2VydmUiPg0KPHBhdGggc3R5bGU9ImZpbGw6IzBBNEVBRjsiIGQ9Ik0yNTYsNTEyYy02OC4zOCwwLTEzMi42NjctMjYuNjI5LTE4MS4wMi03NC45OEMyNi42MjksMzg4LjY2NywwLDMyNC4zOCwwLDI1Ng0KCVMyNi42MjksMTIzLjMzMyw3NC45OCw3NC45OEMxMjMuMzMzLDI2LjYyOSwxODcuNjIsMCwyNTYsMHMxMzIuNjY3LDI2LjYyOSwxODEuMDIsNzQuOThDNDg1LjM3MSwxMjMuMzMzLDUxMiwxODcuNjIsNTEyLDI1Ng0KCXMtMjYuNjI5LDEzMi42NjctNzQuOTgsMTgxLjAyQzM4OC42NjcsNDg1LjM3MSwzMjQuMzgsNTEyLDI1Niw1MTJ6Ii8+DQo8cGF0aCBzdHlsZT0iZmlsbDojMDYzRThCOyIgZD0iTTQzNy4wMiw3NC45OEMzODguNjY3LDI2LjYyOSwzMjQuMzgsMCwyNTYsMHY1MTJjNjguMzgsMCwxMzIuNjY3LTI2LjYyOSwxODEuMDItNzQuOTgNCglDNDg1LjM3MSwzODguNjY3LDUxMiwzMjQuMzgsNTEyLDI1NlM0ODUuMzcxLDEyMy4zMzMsNDM3LjAyLDc0Ljk4eiIvPg0KPHBhdGggc3R5bGU9ImZpbGw6I0ZGRkZGRjsiIGQ9Ik0yNTYsMTg1Yy0zMC4zMjcsMC01NS0yNC42NzMtNTUtNTVzMjQuNjczLTU1LDU1LTU1czU1LDI0LjY3Myw1NSw1NVMyODYuMzI3LDE4NSwyNTYsMTg1eiBNMzAxLDM5NQ0KCVYyMTVIMTkxdjMwaDMwdjE1MGgtMzB2MzBoMTQwdi0zMEgzMDF6Ii8+DQo8Zz4NCgk8cGF0aCBzdHlsZT0iZmlsbDojQ0NFRkZGOyIgZD0iTTI1NiwxODVjMzAuMzI3LDAsNTUtMjQuNjczLDU1LTU1cy0yNC42NzMtNTUtNTUtNTVWMTg1eiIvPg0KCTxwb2x5Z29uIHN0eWxlPSJmaWxsOiNDQ0VGRkY7IiBwb2ludHM9IjMwMSwzOTUgMzAxLDIxNSAyNTYsMjE1IDI1Niw0MjUgMzMxLDQyNSAzMzEsMzk1IAkiLz4NCjwvZz4NCjxnPg0KPC9nPg0KPGc+DQo8L2c+DQo8Zz4NCjwvZz4NCjxnPg0KPC9nPg0KPGc+DQo8L2c+DQo8Zz4NCjwvZz4NCjxnPg0KPC9nPg0KPGc+DQo8L2c+DQo8Zz4NCjwvZz4NCjxnPg0KPC9nPg0KPGc+DQo8L2c+DQo8Zz4NCjwvZz4NCjxnPg0KPC9nPg0KPGc+DQo8L2c+DQo8Zz4NCjwvZz4NCjwvc3ZnPg0K)](https://github.com/UjjwalSaini07/OllamaMulti-RAG/blob/main/README.md)
[![Generic badge](https://img.shields.io/badge/Owner-@Ujjwal-<COLOR>.svg)](https://github.com/UjjwalSaini07/OllamaMulti-RAG)
[![GitHub stars](https://img.shields.io/github/stars/UjjwalSaini07/OllamaMulti-RAG?style=social&label=Star&maxAge=2592100)](https://github.com/UjjwalSaini07/OllamaMulti-RAG/stargazers)
[![Github Release](https://img.shields.io/github/v/release/UjjwalSaini07/OllamaMulti-RAG)](https://github.com/UjjwalSaini07/OllamaMulti-RAG)

## 🚀 Key Features
- **📖 Document Chat (PDF RAG)** → Upload PDFs and extract context-aware insights.  
- **🖼️ Image Analysis** → Unlock hidden stories from visual data.  
- **🎤 Audio to Text** → Record or upload audio and let Whisper transcribe in seconds.  
- **💬 Persistent Chat Sessions** → Store, manage, and reload previous conversations.  
- **⚡ Redis Caching** → Lightning-fast performance with session-level caching.  
- **🎯 Model Flexibility** → Switch easily between **Ollama** and **OpenAI models**.  
- **🔐 Secure by Design** → Environment variables, `.env.sample`, and Dockerized deployment.  
- **📊 Optimized Vector Storage** → ChromaDB-backed semantic search for documents.  
- **🎨 Modern UI** → Built with Streamlit, responsive and minimal.

## 📽️ Demo
Coming soon... 🎬  
> [!IMPORTANT]  
> Use the Docker image or run the project locally via `localhost` to get started.
Before proceeding, please contact me at [Mail](mailto:ujjwalsaini0007+ollama@gmail.com)
so I can share the credentials instead Docker extract your whole memory.

## 🛠️ Technology Stack
- **Frontend/UI** → [Streamlit](https://streamlit.io/)  
- **LLMs & Embeddings** → [Ollama](https://ollama.com/) + [OpenAI](https://platform.openai.com/)  
- **Audio Transcription** → [Whisper](https://openai.com/research/whisper)  
- **Vector Database** → [ChromaDB](https://www.trychroma.com/)  
- **Caching & Session Store** → [Redis Cloud](https://redis.io/)  
- **Containerization** → [Docker](https://www.docker.com/) + Docker Compose  
- **Web Server** → [NGINX](https://nginx.org/) (reverse proxy & static serving)  
- **Database** → SQLite (lightweight local DB for session caching)  
- **Orchestration** → GitHub Actions + Dependabot for CI/CD  

## Getting Started ⚙️
### Prerequisites

Before setting up **Neura-Nix**, make sure you have the following installed:

- **Python 3.10+** → Required for running the backend (tested on `3.10.12`).
- **Docker & Docker Compose** → Preferred method for containerized deployment. [Install Docker](https://docs.docker.com/get-docker/)
- **Git** → For cloning and managing the repository.  [Install Git](https://git-scm.com/downloads).
- **Redis (Cloud or Local)** → Used for caching and optimizing performance.  
  Sign up for [Redis Cloud](https://redis.com/try-free/) or run a local instance.
- **Ollama** → Required for running local multimodal models.  
  - [Download Ollama Desktop](https://ollama.com/download) (Windows/macOS)  
  - Or [install manually on Linux](https://github.com/ollama/ollama)

- **(Optional) GPU Support** → If available, install NVIDIA drivers + CUDA toolkit for accelerated model performance.

⚡ *Tip:* Ensure environment variables (like `REDIS_HOST`, `REDIS_PORT`, `OPENAI_API_KEY`) are properly configured in your `.env` file before running the project.

## Installation 🛠️
You can follow the official setup guide for **Linux, Windows, and Docker** below to run **Neura-Nix {OllamaMulti-RAG}** locally.  

- First Read this [License](https://github.com/UjjwalSaini07/OllamaMulti-RAG/blob/main/LICENSE) & their terms then proceed.
- Star ⭐ the [Repository](https://github.com/UjjwalSaini07/OllamaMulti-RAG)
- Fork the repository **(Optional)**
- Project Setup:
1. Clone the repository:
```bash
    git clone https://github.com/UjjwalSaini07/OllamaMulti-RAG.git
```
2. Navigate to the project main directory:
```bash
    cd NexGen-Quillix
```

> [!IMPORTANT]  
> All these cd directory paths are relative to the root directory of the cloned project.

After Cloning the repository and choose your preferred installation method.  

### 🔹 Method 1: Docker Compose {Not Fastest Step}

1. Modify Docker Compose →  
   - Remove `docker-compose.yml`.  
   - Rename `docker-compose_with_ollama.yml` → `docker-compose.yml`.  
2. **Set model save path** → Update line `21` in the `docker-compose.yml` file.  
3. **Run Neura-Nix**  
   ```bash
     docker compose up
   ```  
   ⚡ If you don’t have a GPU → remove the `deploy` section from the compose file.  

4. **Optional Configurations**  
   - Edit `config.yaml` to match your needs.  
   - Add custom icons → replace `user_image.png` and/or `bot_image.png` inside the `chat_icons` folder.  

5. **Access the app** → Open [http://0.0.0.0:8501](http://0.0.0.0:8501) in your browser.  

6. **Pull Models** → Visit [Ollama Library](https://ollama.com/library) and pull models:  
   ```bash
     /pull MODEL_NAME
   ```  
   ✅ You need:  
   - An **embedding model** → e.g., [nomic-embed-text](https://ollama.com/library/nomic-embed-text) for PDFs.  
   - An **image-capable model** → e.g., [llava](https://ollama.com/library/llava) for image analysis.  

### 🔹 Method 2: Windows (Best Performance)  

⚠️ Using Ollama inside Docker on Windows can be slow → prefer **local installation**.  

1. Install [Ollama Desktop](https://ollama.com/download).  
2. Update config → In `config.yaml`, use **line 4 (Windows)** for `base_url`, remove **line 3** {Default is Correct}.  

3. Start Neura-Nix Up the Docker Container:  
   ```bash
     docker compose up
   ```  
4. Access → [http://0.0.0.0:8501](http://0.0.0.0:8501).  
5. Pull models as prescribed in Method 1.  

### 🔹 Method 3: Manual Install  

1. Install [Ollama](https://github.com/ollama/ollama).  
2. Create Python venv (tested with `Python 3.10.12`).  
3. Install dependencies:  
   ```bash
     pip install --upgrade pip
     pip install -r requirements.txt
     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
   ```  
4. Run setup:  
   ```bash
     python3 database_operations.py   # initialize SQLite DB
     streamlit run app.py
   ```  
5. Pull models (embedding + multimodal as above).  
6. Optional → update `config.yaml` and add custom chat icons.  

## 📊 Business Optimization  

Neura-Nix is not just a research tool — it’s built to **optimize workflows and unlock ROI**:  

- 🏢 **Enterprise Teams** → Automate document review, compliance checks, and data-heavy workflows.  
- 📈 **Startups** → Accelerate content creation, customer support, and product research.  
- 👨‍💻 **Freelancers & Creators** → Boost productivity with multimodal AI (chat, docs, media).  
- 🔒 **Privacy by Design** → Keep your sensitive data secure with local-first deployment.  

## 📚 Documentation

To help you navigate and extend **Neura-Nix**, we’ve structured the documentation into multiple layers:
- [Python Documentation](https://docs.python.org/3/)  
- [Streamlit Documentation](https://docs.streamlit.io/)  
- [Ollama Documentation](https://github.com/ollama/ollama)  
- [OpenAI API Documentation](https://platform.openai.com/docs/)  
- [Whisper Models (OpenAI)](https://huggingface.co/collections/openai/whisper-release-6501bba2cf999715fd953013)  
- [Redis Documentation](https://redis.io/docs/)  
- [ChromaDB Documentation](https://docs.trychroma.com/)  
- [Docker Documentation](https://docs.docker.com/)  
- [Nginx Documentation](https://nginx.org/en/docs/)  
- [GitHub Actions Documentation](https://docs.github.com/en/actions)  

## Author ✍️
- [@Ujjwal Saini](https://github.com/UjjwalSaini07)

## Contact 📞
Feel free to reach out if you have any questions or suggestions!

- Raise an issue for the same [Issue](https://github.com/UjjwalSaini07/OllamaMulti-RAG/issues/new)
- Github: [@Ujjwal Saini](https://github.com/UjjwalSaini07)
- Mail: [Mail ID](mailto:ujjwalsaini0007+ollama@gmail.com)

## License 📄
License Credential [Check](https://github.com/UjjwalSaini07/OllamaMulti-RAG/blob/main/LICENSE). </br>You can use this project the way you want. Feel free to credit me if you want to!

## Feedback and Contributions 💌
Feedback and contributions are always welcome! Feel free to open an [Issue](https://github.com/UjjwalSaini07/OllamaMulti-RAG/issues).

<p align="left">
    <span>Show Some Love</span>
    <img src="https://i.pinimg.com/originals/ca/97/bd/ca97bde328433c2497b154afdee5f8d7.gif" alt="Heart Icon" style="width: 18px; height: 19px;margin-top: 2px; vertical-align: middle;" />
    <span>by Starring the repository and Share this product! </span>
    <img src="https://github.com/user-attachments/assets/059ee3d9-d8ea-4b9a-986d-c9c8e9f47f40" alt="Animation - 1723091871778" style="vertical-align:middle; margin-left: 5px; margin-top: -14px;" />
</p>

<div align="center">
    <a href="#top">
        <img src="https://img.shields.io/badge/Back%20to%20Top-000000?style=for-the-badge&logo=github&logoColor=white" alt="Back to Top">
    </a>
</div>
