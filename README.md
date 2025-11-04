# Multi-Tool AI Assistant with RAG and Text-to-SQL

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?logo=streamlit)](https://streamlit.io/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C?logo=pytorch)](https://pytorch.org/)
[![Qwen-Agent](https://img.shields.io/badge/Qwen-Agent-orange)](https://github.com/modelscope/qwen-agent)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-FFD21E?logo=huggingface)](https://huggingface.co/)
[![Ollama](https://img.shields.io/badge/Ollama-AI-000000?logo=ollama)](https://ollama.ai/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector_Search-0055A4?logo=facebook)](https://github.com/facebookresearch/faiss)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)

An advanced, local-first AI assistant that uses a tool-based agent architecture to answer questions from multiple sources, including a multi-modal RAG knowledge base, a SQL database, and external APIs.

## Features

- **Intelligent Agent with Function Calling**: Uses the Qwen Agent framework with advanced function calling capabilities to understand user intent and automatically route queries to the correct specialized tool.
- **Advanced Text-to-SQL**: Converts natural language questions into SQL queries to fetch data from a PostgreSQL database, enabling non-technical users to query structured data with plain English.
- **Multi-modal RAG**: Retrieves information from text documents (.docx, .pdf, .txt) and images to answer questions.
- **Live Weather Tool**: Connects to an external API to provide real-time weather forecasts.
- **Dual Interface Design**: Separate admin and user interfaces for a clean and focused user experience.
- **Drag & Drop Upload**: Intuitive file upload for building and extending the knowledge base.
- **Incremental Updates**: Add new documents and images without rebuilding the entire vector store.

## Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) for responsive web interfaces.
- **Backend**: Python 3.8+ with modern ML libraries.
- **Agent Framework**: [Qwen Agent](https://github.com/modelscope/qwen-agent) for tool selection and orchestration with advanced **Function Calling** capabilities.
- **Text-to-SQL**: Natural language to SQL query conversion enabling database querying with human language.
- **LLM**: Pluggable local models via [Ollama](https://ollama.ai/) for generation and reasoning.
- **Vector Search**: [FAISS](https://github.com/facebookresearch/faiss) for efficient similarity search in the knowledge base.
- **Database**: [PostgreSQL](https://www.postgresql.org/) for structured data querying via the Text-to-SQL tool.
- **Embeddings**: [Sentence Transformers](https://www.sbert.net/) and [CLIP](https://openai.com/research/clip) models for text and image vectorization.
- **OCR**: [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) for image text extraction.

## Architecture Overview

The system uses a central Query Router (Agent) to delegate tasks to a set of specialized tools.

### Admin Interface (Port 8502)
- **Knowledge Base Management**: Upload documents and images to the RAG tool's knowledge source.
- **Content Processing**: Converts files into vector representations for retrieval.
- **Storage Management**: Builds and updates the FAISS vector database.

### User Interface (Port 8501)  
- **Chat Experience**: Interactive question-answering interface.
- **Query Router**: An agent that directs user queries to the most appropriate tool (RAG, SQL, or Weather).
- **Tools**:
    - **RAG Tool**: Answers questions by retrieving from the vectorized knowledge base.
    - **SQL Tool**: Answers questions by querying a PostgreSQL database.
    - **Weather Tool**: Answers questions by calling a live weather API.

### Core Components Flow
```
┌─────────────────┐    ┌────────────────────┐    ┌─────────────────┐
│   Admin Panel   │───▶│ Knowledge Base    │───▶│  Vector Store   │
│ (Upload Files)  │    │  (Process Files)   │    │   (FAISS DB)    │
└─────────────────┘    └────────────────────┘    └─────────────────┘
                                 ▲                          │
                                 │                          │
┌─────────────────┐    ┌────────┴────────┐    ┌────────────▼──────────────┐
│   User Chat     │───▶│   Query Router  │───▶│ Tools (RAG, SQL, Weather) │
│  (Questions)    │    │  (Agent)        │    │   (Ollama/Llama3.2)       │
└─────────────────┘    └─────────────────┘    └───────────────────────────┘
```

## Example Questions

The assistant can now handle a wider variety of questions. Try asking:

- **RAG / Knowledge Base:**
  - "What are the ticket rules for Shanghai Disneyland?"
  - "Recommend some Disney travel guides."
  - "Show me a picture of the Halloween event poster."
- **Text-to-SQL:**
  - "How many people visited yesterday?"
  - "What was the month with the highest visitor flow?"
- **Weather Tool:**
  - "What's the weather like in Shanghai tomorrow?"

To customize the RAG knowledge base for your own domain, use the Admin Interface to upload your documents and rebuild.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running locally
- [PostgreSQL](https://www.postgresql.org/) installed and running (or accessible via a connection string).
- Required Python packages: `pip install -r requirements.txt`

### Installation

1. Clone the repository:
```bash
git clone https://github.com/monodara/RAG-build-it-yourself.git
cd RAG-build-it-yourself
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

### Running the Application

#### Start Admin Interface (Port 8502)
The admin interface is used for building and managing the RAG knowledge base.

```bash
streamlit run admin_interface/admin_manager.py --server.port 8502
```

![Admin Dashboard](./assets/screenshots/admin_dashboard.png)
*Admin interface showing file upload areas and knowledge base management tools*

#### Start User Interface (Port 8501)
The user interface provides the chat experience with the multi-tool assistant.

```bash
streamlit run user_interface/main.py
```

![Quick Questions](./assets/screenshots/user_quick_question.png)
![User Chat](./assets/screenshots/user_chat.png)
*User chat interface with conversation history and quick question suggestions*

## Usage Workflow
### Admin

1. **Build Knowledge Base**: Use the admin interface (port 8502) to upload documents and images for the RAG tool.
2. **Choose Operation**: Select between rebuilding or incrementally updating the knowledge base.
3. **Execute**: Click "Execute Operation" to process your content.
### User
1. **Interact**: Visit the user interface (port 8501) to chat with the assistant. Ask about topics in your knowledge base, database, or the weather.
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
SYSTEM_ROLE=You are a professional assistant

# --- NEW: Tool Configurations ---
# PostgreSQL connection for SQL Tool
POSTGRES_CONNECTION_STRING=postgresql://user:password@host:port/database

# OpenWeatherMap API Key for Weather Tool
OPENWEATHER_API_KEY=your_api_key_here
```

## System Limitations

While this system provides powerful local capabilities, there are several important limitations to consider:

### Performance Constraints

- **Slow Vectorization Process**: Using local offline models for embedding generation is significantly slower than cloud-based solutions.
- **Limited Accuracy**: Small local models provide lower accuracy compared to larger hosted models.
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
