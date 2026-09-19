# AI Engineering Assistant

A production-oriented AI assistant demonstrating modern LLM engineering concepts including hosted LLM APIs, structured outputs, tool calling, Retrieval-Augmented Generation (RAG), vector search, reranking, open-source model serving with vLLM, provider routing, and Docker containerization.

This project was developed as part of the **Week 15 Applied AI assignment — Task 1: Build an AI Assistant**.

---

## 1. Project Overview

The assistant supports two LLM providers:

- **Gemini** — hosted LLM provider
- **Qwen3-4B** — open-source LLM served using **vLLM**

It also includes a document-grounded RAG pipeline capable of retrieving information from PDF documents and generating answers supported by retrieved evidence.

The system demonstrates:

- Prompt engineering
- Temperature and `top_p` control
- Structured JSON output
- Tool/function calling
- PDF document ingestion
- Chunking with overlap
- Embedding generation
- ChromaDB vector storage
- Semantic retrieval
- Retrieval rejection guardrail
- Cross-encoder reranking
- Grounded generation
- Multiple LLM providers
- vLLM model serving
- Docker containerization

---

## 2. High-Level Architecture

```text
                         User Question
                              |
                              v
                       +--------------+
                       | Model Router |
                       +------+-------+
                              |
                  +-----------+-----------+
                  |                       |
                  v                       v
          +---------------+       +---------------+
          | Gemini API    |       | vLLM Server   |
          | Hosted LLM    |       | Qwen3-4B      |
          +---------------+       +-------+-------+
                                          |
                                          v
                                    NVIDIA GPU
```

### RAG Pipeline

```text
PDF Documents
     |
     v
Text Extraction
     |
     v
Chunking
     |
     v
Embedding Model
all-MiniLM-L6-v2
     |
     v
ChromaDB
     |
     v
Top-10 Semantic Retrieval
     |
     v
Distance Guardrail
     |
     v
Cross-Encoder Reranker
     |
     v
Top-3 Evidence Chunks
     |
     v
Gemini
     |
     v
Grounded Answer + Sources
```

---

## 3. Project Structure

```text
ai_assistant/
│
├── app/
│   ├── __init__.py
│   ├── llm.py
│   ├── local_llm.py
│   ├── model_router.py
│   ├── schemas.py
│   ├── tools.py
│   ├── tool_agent.py
│   │
│   └── rag/
│       ├── __init__.py
│       ├── ingest.py
│       ├── embedder.py
│       ├── vector_store.py
│       ├── reranker.py
│       ├── rag_pipeline.py
│       └── retrieval_diagnostics.py
│
├── data/
│   └── documents/
│       └── sample.pdf
│
├── notebooks/
│   └── W15_vLLM_Colab_Server.ipynb
│
├── docs/
│   └── architecture.png
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── requirements.txt
├── requirements-docker.txt
└── README.md
```

> `.env`, `.venv/`, `__pycache__/`, and `data/chroma_db/` should not be committed.

---

## 4. Core Components

### 4.1 Gemini Hosted LLM

Gemini is used as the hosted model provider.

The implementation includes:

- system prompt engineering
- structured Pydantic output
- JSON schema validation
- confidence scoring
- grounded RAG generation

Example:

```python
result = ask_llm(
    "Explain retrieval augmented generation."
)
```

### 4.2 Qwen3-4B Through vLLM

The project also supports the open-source model:

```text
Qwen/Qwen3-4B
```

served using:

```text
vLLM
```

vLLM exposes an OpenAI-compatible API.

The local-model client connects using:

```python
client = OpenAI(
    base_url=f"{VLLM_BASE_URL}/v1",
    api_key=VLLM_API_KEY,
)
```

The `openai` Python package is used only as an API client. The actual model being served is **Qwen3-4B**.

---

## 5. Prompt Engineering

The project uses system prompts to control:

- response style
- grounding behavior
- structured output
- source usage
- hallucination resistance

The open-source model also demonstrates explicit generation parameters:

```python
temperature = 0.7
top_p = 0.8
```

### Temperature

Controls randomness during token generation.

```text
Lower temperature
→ more deterministic

Higher temperature
→ more varied
```

### Top-p

Limits sampling to the most probable tokens whose cumulative probability reaches the specified threshold.

---

## 6. Structured Output

Gemini responses are validated with **Pydantic**.

Example schema:

```python
class AssistantResponse(BaseModel):
    answer: str
    confidence: float
```

The RAG pipeline also returns structured fields such as:

- answer
- source IDs
- confidence

This helps ensure predictable machine-readable outputs.

---

## 7. Tool Calling

The assistant supports function/tool calling.

Implemented tools include:

### Calculator

Supported operations:

- add
- subtract
- multiply
- divide

Example request:

```text
81 divided by 9
```

The model selects:

```text
Tool: calculate

Arguments:
a = 81
b = 9
operation = divide
```

Python executes the tool and returns the result to the model.

### Word Counter

Example:

```text
Count the words in:
"Artificial intelligence is changing modern software development"
```

The tool executes:

```python
count_words(...)
```

and returns the computed word count.

---

## 8. Retrieval-Augmented Generation

The RAG pipeline allows the assistant to answer questions using external PDF documents.

### 8.1 Document Ingestion

PDF text is extracted page-by-page using:

```text
pypdf
```

Each page retains:

- source filename
- page number
- extracted text

### 8.2 Chunking

Documents are split using:

```text
RecursiveCharacterTextSplitter
```

Configuration:

```text
Chunk size:     800 characters
Chunk overlap:  120 characters
```

The overlap helps preserve context between neighboring chunks.

Stable chunk IDs follow:

```text
filename:page:chunk_index
```

Example:

```text
sample.pdf:7:2
```

### 8.3 Embeddings

Embedding model:

```text
sentence-transformers/all-MiniLM-L6-v2
```

Embedding size:

```text
384 dimensions
```

Both document chunks and user queries use the same embedding model so their vectors exist in the same semantic space.

Embeddings are normalized before storage.

### 8.4 Vector Database

The project uses:

```text
ChromaDB
```

with cosine distance.

Each stored record contains:

```text
Document text
Embedding vector
Metadata
    source
    page
```

---

## 9. Retrieval Guardrail

Vector databases always return the closest available chunks, even when a question is unrelated.

To reduce irrelevant LLM calls, the system applies an empirical retrieval-distance guardrail.

Observed diagnostic values:

```text
Relevant queries:
0.4495
0.4754
0.6339
0.4725

Unrelated queries:
0.8862
0.8839
0.7923
0.7107
```

Initial threshold:

```text
0.67
```

Logic:

```python
if best_distance > RETRIEVAL_DISTANCE_THRESHOLD:
    reject
```

This helps reduce:

- unnecessary API calls
- latency
- API cost
- hallucination risk

> The threshold is specific to the current embedding model, chunking configuration, document collection, and diagnostic queries. It should be recalibrated if those change.

---

## 10. Cross-Encoder Reranking

Embedding retrieval is fast, but the highest-ranked chunk is not always the most useful chunk.

The project therefore uses two-stage retrieval:

```text
Question
   |
   v
Embedding Search
   |
   v
Top 10 Candidates
   |
   v
Cross-Encoder
   |
   v
Top 3 Chunks
```

Reranker:

```text
cross-encoder/ms-marco-MiniLM-L-6-v2
```

The cross-encoder evaluates the query and candidate chunk together.

Example observed during development:

```text
Correct chunk:

Embedding rank: 9

After reranking:
Rank: 1
```

This improved answer quality for questions where embedding-only top-3 retrieval missed the most useful evidence.

---

## 11. Grounded Generation

The RAG system instructs Gemini to answer only from retrieved document context.

Example:

```text
Question:
Which framework is used for browser automation?
```

Retrieved evidence references:

```text
Playwright
```

The assistant then generates a grounded answer and returns its supporting source.

If sufficient evidence is not found, the system returns a refusal such as:

```text
The available documents do not contain sufficiently
relevant information to answer this question.
```

instead of inventing an answer.

---

## 12. Provider Router

The project exposes a common interface for both providers.

Gemini:

```python
ask_model(
    question="Explain embeddings",
    provider="gemini"
)
```

vLLM / Qwen:

```python
ask_model(
    question="Explain embeddings",
    provider="vllm"
)
```

Architecture:

```text
Application
    |
    v
Model Router
   /     \
  /       \
Gemini    Qwen
          |
         vLLM
```

This abstraction also prepares the project for provider fallback in Task 2.

---

## 13. Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key

VLLM_BASE_URL=https://your-tunnel.trycloudflare.com
VLLM_API_KEY=your_vllm_api_key
VLLM_MODEL=Qwen/Qwen3-4B

DEFAULT_LLM_PROVIDER=gemini
```

Never commit `.env`.

It should be excluded through both:

```text
.gitignore
.dockerignore
```

---

## 14. Local Setup

### 14.1 Create a Virtual Environment

```powershell
python -m venv .venv
```

Activate:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 14.2 Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

---

## 15. Build the Vector Database

Place PDF documents inside:

```text
data/documents/
```

Then run:

```powershell
python -m app.rag.vector_store
```

Example output:

```text
Stored 47 chunks in ChromaDB.
```

---

## 16. Run the RAG Pipeline

```powershell
python -m app.rag.rag_pipeline
```

Example:

```text
Question:
Which framework is used for browser automation?

Answer:
Playwright is used for browser automation.

Confidence:
0.9

Sources:
sample.pdf
```

---

## 17. Test Tool Calling

Run:

```powershell
python -m app.tool_agent
```

The model can select and execute registered Python functions.

---

## 18. Run Qwen3-4B With vLLM

The project includes:

```text
notebooks/W15_vLLM_Colab_Server.ipynb
```

The notebook performs:

```text
GPU Verification
      |
      v
vLLM Installation
      |
      v
Qwen3-4B Loading
      |
      v
OpenAI-Compatible API
      |
      v
Temporary Cloudflare Tunnel
```

Development inference was tested on an NVIDIA L4 GPU in Google Colab.

The notebook also generates an API key for the vLLM endpoint before exposing it through the temporary tunnel.

> The Cloudflare Quick Tunnel is intended only for development/demo use. The tunnel URL changes when the tunnel or Colab runtime restarts.

---

## 19. Test the Open-Source LLM

Once the vLLM server and tunnel are running:

```powershell
python -m app.local_llm
```

Example:

```text
Local LLM response:
Vector databases are specialized databases designed
to store and search high-dimensional vector data efficiently.
```

---

## 20. Test Both Providers

Run:

```powershell
python -m app.model_router
```

Example:

```text
--- Gemini ---

Provider: gemini
Model: gemini-3.6-flash
Answer: ...


--- Local vLLM ---

Provider: vllm
Model: Qwen/Qwen3-4B
Answer: ...
```

---

## 21. Docker

### 21.1 Build the Image

```powershell
docker build -t ai-assistant-task1 .
```

### 21.2 Create Persistent Chroma Storage

```powershell
docker volume create ai-assistant-chroma
```

### 21.3 Index Documents Inside Docker

```powershell
docker run --rm `
  -v ai-assistant-chroma:/app/data/chroma_db `
  ai-assistant-task1 `
  python -m app.rag.vector_store
```

### 21.4 Run the RAG Pipeline Inside Docker

```powershell
docker run --rm `
  --env-file .env `
  -v ai-assistant-chroma:/app/data/chroma_db `
  ai-assistant-task1
```

### 21.5 Test Qwen/vLLM From Docker

```powershell
docker run --rm `
  --env-file .env `
  ai-assistant-task1 `
  python -m app.local_llm
```

### 21.6 Test Both Providers From Docker

```powershell
docker run --rm `
  --env-file .env `
  ai-assistant-task1 `
  python -m app.model_router
```

---

## 22. Docker Architecture

```text
Docker Container
│
├── Gemini Client
├── Tool Calling
├── RAG Pipeline
├── Embedding Model
├── Cross-Encoder Reranker
├── ChromaDB Client
├── Model Router
└── vLLM Client
        |
        +------> Gemini API
        |
        +------> External vLLM Server
                      |
                      v
                  Qwen3-4B
```

Chroma data is persisted using a Docker named volume rather than being stored only inside an ephemeral container.

---

## 23. Recommended `.gitignore`

```gitignore
# Virtual environments
.venv/
venv/

# Secrets
.env
.env.*

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd

# Generated Chroma database
data/chroma_db/

# IDE files
.vscode/
.idea/

# Jupyter checkpoints
.ipynb_checkpoints/

# Logs
*.log

# Build artifacts
build/
dist/
*.egg-info/

# Test/cache files
.pytest_cache/
.mypy_cache/
.coverage

# OS files
.DS_Store
Thumbs.db
```

---

## 24. Task 1 Requirement Coverage

| Requirement | Implementation |
|---|---|
| Major LLM provider | Gemini |
| Prompt engineering | System prompts |
| Temperature / `top_p` | Qwen generation configuration |
| Structured JSON | Pydantic + Gemini structured output |
| Tool calling | Calculator + word counter |
| Document ingestion | `pypdf` |
| Chunking | `RecursiveCharacterTextSplitter` |
| Embeddings | `all-MiniLM-L6-v2` |
| Vector database | ChromaDB |
| RAG | Grounded document QA |
| Retrieval guardrail | Cosine-distance threshold |
| Reranking | Cross-encoder |
| Open-source model | Qwen3-4B |
| Model serving | vLLM |
| Provider abstraction | Model Router |
| Containerization | Docker |

---

## 25. Task 1 Deliverables

Task 1 submission contains:

- Source code
- Dockerfile
- README
- Architecture diagram

Supporting reproducibility material also includes:

- `requirements.txt`
- `requirements-docker.txt`
- `.dockerignore`
- `.gitignore`
- vLLM Colab notebook
- sample PDF used for RAG testing

---

## 26. Current Limitations

The Task 1 version does not yet include:

- Web UI
- FastAPI application backend
- asynchronous request handling
- rate limiting
- automatic retries
- automatic Gemini → vLLM fallback
- production caching
- Docker Compose deployment

These are planned for **Task 2 — Productionize the AI Assistant**.

---

## 27. Task 2 Roadmap

The productionized version will extend the current architecture:

```text
Streamlit UI
     |
     v
FastAPI Backend
     |
     v
RAG + Model Router
     |
     +---- Gemini
     |
     +---- Qwen/vLLM
```

Planned production features:

- web UI
- backend API
- asynchronous/concurrent request handling
- latency and throughput measurement
- retry mechanism
- rate limiting
- provider/model fallback
- graceful degradation
- optional prompt/response caching
- Docker Compose deployment

---

## 28. Security Notes

- Never commit `.env`.
- Never commit API keys.
- The public vLLM tunnel is temporary and should only be used for development/demo purposes.
- Generated Chroma storage is excluded from Git because it can be rebuilt from source documents.
- Use environment variables for all provider credentials.

---

## 29. Summary

This Task 1 implementation demonstrates a complete applied-AI workflow combining:

```text
Hosted LLM
+ Open-Source LLM
+ Tool Calling
+ RAG
+ Embeddings
+ Vector Database
+ Retrieval Guardrails
+ Cross-Encoder Reranking
+ Provider Routing
+ vLLM Serving
+ Docker
```

The result is a modular AI-assistant foundation that can be extended into a production-ready application in Task 2.
