# 🔍 Document Search System with PostgreSQL + pgvector

A Docker-powered RAG (Retrieval Augmented Generation) system that lets you search through your documents using semantic similarity. Built with PostgreSQL, pgvector, and LangChain.

## 🚀 Quick Start

1. **Clone and setup:**
   ```bash
   git clone <your-repo>
   cd document-search-system
   ```

2. **Add your documents:**
   ```bash
   mkdir documents
   # Add your .txt or .md files to the documents/ directory
   cp your-policies.txt documents/
   cp your-handbook.md documents/
   ```

3. **Start the system:**
   ```bash
   docker compose up
   # bash into container
   make bash
   # spin up app manually
   python rag-app.py
   ```

4. **Start searching!** The app will automatically:
   - Start PostgreSQL with pgvector extension
   - Load and process your documents
   - Create semantic embeddings
   - Launch the interactive search interface

## 📁 Project Structure

```
.
├── docker-compose.yml      # Docker orchestration
├── Dockerfile             # Python app container
├── rag_search.py          # Main application
├── requirements.txt       # Python dependencies
├── init.sql              # PostgreSQL initialization
├── documents/            # 📂 Put your .txt/.md files here
├── data/                 # 💾 Persistent data (hash files)
└── README.md
```

## ✨ Features

- **🐳 Fully Dockerized** - No local setup required
- **💾 Persistent Database** - Vector database survives container restarts
- **🧠 Smart Rebuilding** - Only rebuilds when documents change
- **📄 Multi-format** - Supports .txt and .md files
- **🎯 Semantic Search** - Find documents by meaning, not just keywords
- **🎨 Colorful Interface** - Easy-to-read terminal output
- **📊 Similarity Scores** - See how relevant each result is

## 🔧 Usage

1. **Add documents** to the `./documents/` directory
2. **Run** `docker compose up`
3. **Ask questions** like:
   - "What is the vacation policy?"
   - "How do I submit expenses?"
   - "What are the remote work guidelines?"

## 🏗️ Architecture

- **PostgreSQL + pgvector**: Persistent vector database
- **sentence-transformers**: Creates semantic embeddings
- **LangChain**: Document processing and retrieval
- **Docker**: Containerized deployment

## 📝 Example Session

```
🔍 Document Search System (PostgreSQL + pgvector)
🐳 Running in Docker container
============================================================
Found 2 files: company-policies.txt, employee-handbook.md
✓ Documents unchanged, using existing database
✅ Connected to existing database
✅ System ready! Your vector database persists in PostgreSQL.

============================================================
Enter your question about the documents: What is the vacation policy?
How many similar results do you want? (default=3): 

🔍 Searching PostgreSQL vector database for 'What is the vacation policy?'...

============================================================
QUESTION: What is the vacation policy?
============================================================

--- RESULT 1 ---
Distance Score: 0.234 (lower = more similar)
Content: Vacation Policy: All full-time employees are entitled to 15 days of paid vacation per year...
Source: documents/company-policies.txt
```

## 🔄 Updating Documents

1. Add new files to `./documents/` directory
2. Restart containers: `docker compose restart`
3. The system automatically detects changes and rebuilds the database

## 🛠️ Customization

**Change chunk size:**
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,  # Increase for longer chunks
    chunk_overlap=40,
)
```

**Use different embedding model:**
```python
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"  # More accurate but slower
)
```

**Modify database connection:**
Update the `DATABASE_URL` environment variable in `docker-compose.yml`

## 🐛 Troubleshooting

**Database connection issues:**
```bash
docker compose logs postgres
```

**Python app issues:**
```bash
docker compose logs rag-app
```

**Reset everything:**
```bash
docker compose down -v  # Removes volumes
docker compose up --build
```

## 📦 Dependencies

- PostgreSQL 16 with pgvector extension
- Python 3.11
- LangChain + LangChain Community
- sentence-transformers
- psycopg2-binary

## 🤝 Contributing

1. Fork the repo
2. Add your documents to test
3. Submit issues or improvements!

---

**Built with ❤️ using PostgreSQL, pgvector, and LangChain**
