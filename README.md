# Multi-Modal AI Assistant for Theme Park Operations

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?logo=pytorch)](https://pytorch.org/)
[![Qwen-Agent](https://img.shields.io/badge/Qwen-Agent-orange)](https://github.com/modelscope/qwen-agent)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-FFD21E?logo=huggingface)](https://huggingface.co/)
[![Ollama](https://img.shields.io/badge/Ollama-AI-000000?logo=ollama)](https://ollama.ai/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector_Search-0055A4?logo=facebook)](https://github.com/facebookresearch/faiss)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)

An advanced, multi-modal AI assistant system for a theme park, integrating ```RAG```, ```Text2SQL```, ```Function Calling```, and ```MCP (Model Context Protocol)``` that can answer questions related to visiting tips, previous flows, transportation routes, weather information, etc.

## Features

- **Intelligent Multi-Tool Agent**: Uses the Qwen Agent framework with advanced function calling capabilities to intelligently route queries across multiple specialized tools.
- **Multi-Modal RAG**: Retrieves information from text documents (.docx, .pdf, .txt) and images to answer operational and informational queries.
- **Text-to-SQL for Data Insights**: Converts natural language questions into SQL queries to extract visitor flow statistics and seasonal trends from PostgreSQL database.
- **Real-Time Weather Integration**: Connects to external ```OpenWeather``` APIs to provide current,forecast or historical weather information for visiting planning.
- **Google Map MCP**: Provides route planning and location-based information.
- **Dual Interface Design**: Separate admin and user interfaces for knowledge base management and end-user interaction.
- **Drag & Drop Upload**: Intuitive file upload for building and extending the knowledge base with park documents, policies, and media.
- **Incremental Updates**: Add new documents and images without rebuilding the entire vector store.

## Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) for responsive web interfaces.
- **Backend**: Python 3.8+ & FastAPI.
- **Agent Framework**: [Qwen Agent](https://github.com/modelscope/qwen-agent) for intelligent tool selection and orchestration with advanced **Function Calling** capabilities.
- **Text-to-SQL**: Natural language to SQL query conversion enabling database querying with human language.
- **LLM**: Pluggable local models via [Ollama](https://ollama.ai/) for generation and reasoning.
- **Vector Search**: [FAISS](https://github.com/facebookresearch/faiss) for efficient similarity search in the knowledge base.
- **Database**: [PostgreSQL](https://www.postgresql.org/) for structured data querying (visitor flow).
- **Embeddings**: [Sentence Transformers](https://www.sbert.net/) and [CLIP](https://openai.com/research/clip) models for text and image vectorization.
- **OCR**: [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) for image text extraction.
- **MCP**: [Model Context Protocol](https://modelcontextprotocol.dev/) for enhanced tool integration and model interaction with Google Maps services.

## Architecture Overview

The system uses an intelligent query router (agent) to distribute requests across specialized tools based on user intent.

- **Intelligent Query Router**: Agent that automatically routes queries to the most appropriate tool (RAG, SQL, Weather, or MAP).
- **Multi-Tool Suite**:
    - **RAG Tool**: Answers  questions by retrieving from the vectorized knowledge base.
    - **SQL Tool**: Convert the query into SQL,execute SQL, and analyzes query results.
    - **Weather Tool**: Provides weather info for visit planning.
    - **Map Services**: Offers route planning and location-based information via Google Maps MCP.

```
┌──────────────────┐    ┌────────────────────┐    ┌──────────────────────────┐
│    User Query    │───▶│   Query Router     │───▶│          Tools           │
│                  │    │     (Agent)        │    │ (Weather / SQL / RAG /   │
└──────────────────┘    └────────────────────┘    │           Maps)          │
                                                  └───────────┬──────────────┘
                                                              │
                                                              ▼
                                              ┌─────────────────────────────┐
                                              │           LLM               │
                                              │  Combine tool results → NL  │
                                              └───────────┬─────────────────┘
                                                          │
                                                          ▼
                                              ┌──────────────────────────────┐
                                              │       Final Answer           │
                                              │ (Natural Language Output)    │
                                              └──────────────────────────────┘
```
![Agent](./assets/architecture/agent.png)

## RAG Architecture
![RAG](./assets/architecture/RAG-architecture.png)

The RAG (Retrieval-Augmented Generation) architecture consists of several key components:

- **Document Ingestion Pipeline**: Processes various document formats (PDF, DOCX, TXT) and images using specialized parsers with OCR capabilities for image text extraction.
- **Embedding Engine**: Generates vector embeddings using Sentence Transformers for text content and CLIP models for images, creating semantic representations for similarity search.
- **Vector Storage**: FAISS-based vector database that stores document chunks with metadata for efficient similarity search and retrieval.
- **Retrieval Mechanism**: Multi-modal search that can retrieve both text and image content based on semantic similarity to user queries.
- **Context Augmentation**: Combines retrieved knowledge base content with user queries to provide contextually relevant responses.
- **Knowledge Base Management**: Allows uploading, processing, and incremental updates to the knowledge base through the admin interface.

### Admin Interface for Knowledge Base Management
- **Knowledge Base Management**: Upload operational documents, policies, and park guides to the RAG knowledge base.
- **Content Processing**: Converts files into vector representations for efficient retrieval.
- **Storage Management**: Builds and updates the FAISS vector database.

## Example Questions

The assistant can handle a comprehensive range of theme park visiting queries. Try asking:

- **RAG / Knowledge Base:**
  - "What are the current ticket policies?"
  - "What safety protocols should staff follow?"

- **Text-to-SQL / Data Analytics:**
  - "I wanna avoid peak seasons. What was the months with less visit flow?"

- **Weather Tool:**
  - "I wanna visit the theme park next Sunday. What's the weather like then?"

- **Location Services / MCP:**
  - "What's the best route from XXX to the theme park?"

## Getting Started

### Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running locally
- [PostgreSQL](https://www.postgresql.org/) installed and running (or accessible via a connection string).
- Required Python packages: `pip install -r requirements.txt`

### Installation

1. Clone the repository:
```bash
git clone https://github.com/monodara/Intelligent_QA_Assistant.git
cd Intelligent_QA_Assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env file with your PostgreSQL connection string and API keys
```

### Run the Application

#### Start Backend Server (Port 8000)
First, start the backend server that handles all AI processing, RAG, and tool integration:

```bash
uvicorn bot.server.app:app --host 0.0.0.0 --port 8000 --reload
```

This backend provides the API endpoints for knowledge base management, query processing, and tool orchestration.

#### Start User Interface (Port 8501)
After the backend is running, start the user interface that connects to the backend:

```bash
streamlit run user_interface/main.py
```

![Quick Questions](./assets/screenshots/user_quick_question.png)
![User Chat](./assets/screenshots/user_chat.png)
*User chat interface with conversation history and quick question suggestions*

## Usage Workflow
### Admin

1. **Build Knowledge Base**: Use the admin interface (port 8502) to upload operational documents, policies, and park guides for the RAG tool.
2. **Choose Operation**: Select between rebuilding or incrementally updating the knowledge base.
3. **Execute**: Click "Execute Operation" to process your content.
### User
1. **Interact**: Visit the user interface (port 8501) to chat with the assistant. Ask about operational policies, visitor statistics, weather, or location information.
2. **Update**: Click "Reload Knowledge Base" in the user interface if the admin has made changes.

## Supported Document Formats

### Text Documents
- Microsoft Word: `.docx`
- Portable Document Format: `.pdf`
- Plain Text: `.txt`

### Images
- PNG: `.png`
- JPEG: `.jpg`, `.jpeg`
- Bitmap: `.bmp`
- Graphics Interchange Format: `.gif`

## Configuration

Customize the system through environment variables in your `.env` file:

```bash
# Knowledge base paths
DOCS_DIR=knowledge_base
DATA_DIR=data

# Model configuration
TEXT_EMBEDDING_MODEL=all-MiniLM-L6-v2
CLIP_MODEL_NAME=openai/clip-vit-base-patch32

# Ollama settings
OLLAMA_MODEL=llama3.2:3b
OLLAMA_TEMPERATURE=0.3

# System identity
SYSTEM_NAME=Intelligent Q&A Assistant
SYSTEM_ROLE=You are a professional assistant of a theme park.

# --- Tool Configurations ---
# PostgreSQL connection for SQL Tool
POSTGRES_CONNECTION_STRING=postgresql://user:password@host:port/database

# OpenWeatherMap API Key for Weather Tool
OPENWEATHER_API_KEY=your_api_key_here

# Google Maps API Key for MCP Location Services
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

## System Limitations

While this system provides powerful local capabilities, there are several important limitations to consider:

### Performance Constraints

- **Slow Vectorization Process**: Using local offline models for embedding generation is significantly slower (but resource-saving) than cloud-based solutions.
- **Limited Accuracy**: Small local Ollama small models provide lower accuracy compared to larger hosted models.
- **Resource Intensive**: Model loading and inference consume considerable CPU/memory resources.
- **Response Time**: Answer generation can be slow due to local processing constraints.

### Model Limitations

- **Model Size vs Quality Trade-off**: The project uses smaller models (like all-MiniLM-L6-v2) to enable local execution, which compromises accuracy.
- **Hardware Dependencies**: Performance varies greatly depending on available hardware (CPU vs MPS acceleration).
- **Memory Constraints**: Large knowledge bases may exceed available memory on resource-limited systems.

### Scalability Issues

- **Single Machine Limitation**: Currently designed for single-machine deployment only.
- **Concurrent Users**: Limited support for multiple simultaneous users due to the stateful nature of the Streamlit application.
- **Large Document Processing**: May struggle with very large documents or datasets.

### Recommendation

For production environments requiring high performance and accuracy, consider:
- Using more powerful cloud-based models.
- Implementing GPU acceleration where available.
- Optimizing vector database indexing strategies.
- Implementing caching mechanisms for frequently accessed content.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.