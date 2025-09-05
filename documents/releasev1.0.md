# 🚀 Release Notes – Neura-Nix v1.0.0

**Release Date:** September 5, 2025  
**Repository:** [OllamaMulti-RAG](https://github.com/UjjwalSaini07/OllamaMulti-RAG)  
**Author:** UjjwalS ([ujjwalsaini.dev](https://ujjwalsaini.dev))

## 🎉 Highlights

- **First stable, production-ready release of Neura-Nix: a multimodal AI assistant for text, images, PDFs, and audio.**
- **Containerized deployment with Docker & Docker Compose.**
- **Robust security policy and best practices.**
- **Modular, extensible, and well-documented codebase.**


## ✨ New Features

- **Multimodal Chatbot:**  
	- Seamless interaction with text, images, PDFs, and audio.  
	- Unified chat API handler for both Ollama and OpenAI models.  
	- Real-time chat session management and persistent history (SQLite).  
	- PDF ingestion pipeline with chunking, vector storage (ChromaDB), and retrieval-augmented generation (RAG).  
	- Audio transcription using Whisper ASR and audio file support.  
	- Image analysis and chat integration.

- **Modern UI/UX:**  
	- Built with Streamlit for a responsive, interactive web interface.  
	- Custom chat bubbles, avatars, and sidebar navigation.  
	- File uploaders for PDFs, images, and audio.

- **Scalable Infrastructure:**  
	- Dockerized app and Redis caching for production deployment.  
	- Nginx reverse proxy configuration for secure, scalable access.  
	- Environment variable management and sample `.env` file.

- **Extensibility & Maintainability:**  
	- Modular utilities for model management, prompt templates, and HTML/CSS.  
	- Centralized configuration (`config.yaml`) and metadata.  
	- Python packaging with `pyproject.toml` and `requirements.txt`.

## 🛡️ Security & Best Practices

- **Security Policy:**  
	- v1.0.0 is fully supported for critical fixes.  
	- Responsible disclosure process for vulnerabilities.  
	- Commitment to strong security standards and regular updates.

- **Industrial Practices:**  
	- Structured logging, error handling, and session state management.  
	- Dependency pinning and regular updates.  
	- Clear code ownership and author attribution.  
	- Automated health checks and container orchestration.

## 📝 Upgrade & Usage Notes

- **Deployment:**  
	- Use Docker Compose for local or cloud deployment.  
	- Configure environment variables as per `.env.sample`.  
	- Exposed ports: `8501` (app), `11434` (Ollama), `6379` (Redis).

- **Extending Functionality:**  
	- Add new models or providers by extending the `chat_api_handler`.  
	- Integrate additional file types or data sources via modular utilities.

- **Known Limitations:**  
	- v1.0.0 is feature-complete; new features will be considered for v2.0.0.  
	- Only critical fixes will be backported to v1.0.0.

## 📂 Changelog with Commit IDs

| Commit ID | Summary |
|-----------|---------|
| 1ce22c9 | Update supported versions in SECURITY.md |
| 7e1fbb8 | Update chat and database config parameters |
| e9b1d4e | Add project metadata headers and author tags |
| 705b725 | Add project metadata and update Docker Compose |
| d82e600 | Add Nginx config and startup script for Neura-Nix |
| 16beb01 | Add Docker Compose setup and improve Dockerfile |
| 3bf9187 | Add initial requirements.txt with dependencies |
| 1d611dc | Add main Streamlit app for Neura-Nix assistant |
| cb619e8 | Rename and update .env sample file |
| b21aeb1 | Add utility functions for model management and helpers |
| 331a68f | Rename chatTrack to chatTracking in config and path |
| 5159d60 | Add .gitkeep to track chat session cache directory |
| 54c5843 | Rename Pdf_IngestionPipeline.py to new directory |
| 6b36664 | Move Pdf_IngestionPipeline.py to Ingestion_Pipeline |
| 6c1e441 | Add database operations module for chat messages |
| 817d6b0 | Add user image icon and HTML chat CSS template |
| 3d782a8 | Add unified chat API handler for OpenAI and Ollama |
| bd4ef1e | Add audio handler utility and move vectordb handler |
| 52a1631 | Add vector DB handler and prompt templates |
| f5a6701 | Add PDF ingestion pipeline and basic PDF handler |
| cf7cc85 | Add Logo and BotImage assets |
| 2d40577 | Add initial config, Dockerfile, and sample env file |
| 6bf6196 | Add initial project configuration and security policy |
| a380700 | Adding Apache License 2.0 |
| 8dd871c | Initial commit |

## 🙏 Acknowledgements

Thanks to all contributors and users for feedback and support.  
For issues, feature requests, or security concerns, please use [GitHub Issues](https://github.com/UjjwalSaini07/OllamaMulti-RAG/issues) or contact the maintainer directly.

**Neura-Nix v1.0.0** – Built for clarity, efficiency, and adaptability.

