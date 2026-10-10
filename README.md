# GenAI Production Platform

### Multi-Tenant Agentic RAG API

A Generative AI platform that allows users to upload PDF documents and ask questions about their contents using Retrieval-Augmented Generation (RAG). It combines semantic search, vector embeddings, document retrieval, and LLM-powered answering to generate context-aware responses with source attribution.

**Built with FastAPI, LangGraph, PostgreSQL, Qdrant, and Docker Compose.**

---

## 🚀 Key Features

* **PDF Document Ingestion:** Upload PDF documents through a REST API.
* **Text Extraction and Chunking:** Extract text and split it into smaller chunks.
* **Semantic Search:** Generate embeddings and retrieve relevant document chunks.
* **Retrieval-Augmented Generation:** Generate answers using retrieved document context.
* **Multi-Tenant Isolation:** Filter document retrieval by tenant ID.
* **Evidence Evaluation:** Use a configurable relevance threshold to assess retrieved evidence.
* **Source Attribution:** Return source documents, chunk IDs, relevance scores, and text excerpts.
* **API Authentication:** Protect endpoints using API key authentication.
* **PostgreSQL Persistence:** Store document metadata using SQLAlchemy and Alembic.
* **Vector Database:** Store and search embeddings using Qdrant.
* **Dockerized Deployment:** Run application services using Docker Compose.
* **Health Checks:** Monitor application liveness and readiness.

---

## 🏗️ System Architecture
```mermaid
flowchart TB
    U["Client / API Consumer"]

    subgraph API["API Layer — FastAPI"]
        AUTH["Authentication & Tenant Identification"]
        DOC["Document Upload API"]
        CHAT["Chat API"]
    end

    subgraph INGEST["Document Ingestion Pipeline"]
        PARSE["PDF Text Extraction"]
        CHUNK["Text Chunking"]
        EMBED["Embedding Model"]
        UPSERT["Store Vectors in Qdrant"]
        METADATA["Store Document Metadata in PostgreSQL"]
    end

    subgraph RAG["Agentic RAG Pipeline — LangGraph"]
        RETRIEVE["Retrieve Relevant Chunks"]
        EVAL["Evaluate Evidence Relevance"]
        ROUTE{"Sufficient Evidence?"}
        GENERATE["Generate Answer with LLM"]
        FALLBACK["Return Insufficient-Evidence Response"]
        RESPONSE["Return Answer, Sources & Grounded Status"]
    end

    subgraph STORAGE["Data Layer"]
        QDRANT[("Qdrant — Vector Search")]
        POSTGRES[("PostgreSQL — Document Metadata")]
    end

    LLM["LLM Provider"]

    U --> AUTH
    AUTH --> DOC
    AUTH --> CHAT

    DOC --> PARSE
    PARSE --> CHUNK
    CHUNK --> EMBED
    EMBED --> UPSERT
    UPSERT --> QDRANT
    DOC --> METADATA
    METADATA --> POSTGRES

    CHAT --> RETRIEVE
    RETRIEVE --> QDRANT
    QDRANT --> RETRIEVE
    RETRIEVE --> EVAL
    EVAL --> ROUTE

    ROUTE -->|Yes| GENERATE
    ROUTE -->|No| FALLBACK

    GENERATE <--> LLM
    GENERATE --> RESPONSE
    FALLBACK --> RESPONSE
    RESPONSE --> U

    AUTH -. "Tenant context" .-> RETRIEVE
    AUTH -. "Tenant context" .-> DOC
```

## 🛠️ Technology Stack

| Technology      | Purpose                                  |
| --------------- | ---------------------------------------- |
| Python          | Backend development                      |
| FastAPI         | REST API framework                       |
| LangGraph       | RAG workflow orchestration               |
| PostgreSQL      | Document metadata storage                |
| SQLAlchemy      | Database access and ORM                  |
| Alembic         | Database migrations                      |
| Qdrant          | Vector storage and similarity search     |
| Hugging Face | Generates embeddings using the configured embedding model |
| Docker          | Containerization                         |
| Docker Compose  | Manage application services              |
| Swagger UI      | Interactive API documentation            |
| Groq API        | Provides LLM inference for answer generation |

---

## 🔄 RAG Workflow

1. **Document Upload:** Upload a PDF through the API.
2. **Text Extraction:** Extract text from the PDF.
3. **Chunking:** Divide the extracted text into smaller chunks.
4. **Embedding Generation:** Convert chunks into vector embeddings.
5. **Vector Storage:** Store embeddings and metadata in Qdrant.
6. **Question Processing:** Submit a question to the chat endpoint.
7. **Semantic Retrieval:** Retrieve relevant chunks using vector similarity search.
8. **Evidence Evaluation:** Compare the highest retrieval score against a configurable threshold.
9. **Answer Generation:** Generate an answer using the retrieved context when sufficient evidence is available.
10. **Fallback Handling:** Return an insufficient-information response when evidence does not meet the threshold.
11. **Source Attribution:** Return supporting document information with the answer.

LangGraph coordinates the retrieval, evidence evaluation, and response-generation workflow.

---

## 📁 Project Structure

```text
genai-production-platform/
│
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   └── routes.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   │
│   ├── domain/
│   │   └── schemas.py
│   │
│   ├── graph/
│   │   └── workflow.py
│   │
│   ├── services/
│   │   ├── db.py
│   │   ├── embeddings.py
│   │   ├── ingestion.py
│   │   ├── llm.py
│   │   └── vector_store.py
│   │
│   └── main.py
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Getting Started

### Prerequisites

* Python 3.12 or a compatible version supported by the project
* Docker Desktop
* Docker Compose
* Git
* An API key for the configured LLM provider, if required

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd genai-production-platform
```

### 2. Configure Environment Variables

Create a `.env` file in the project root using `.env.example` as a template.

Example configuration:

```env
GROQ_API_KEY=your-groq-api-key
APP_API_KEY=replace-with-a-strong-secret
DATABASE_URL=postgresql+asyncpg://app:app@postgres:5432/genai
QDRANT_URL=http://qdrant:6333
QDRANT_COLLECTION=knowledge_chunks
MIN_EVIDENCE_SCORE=0.65
```

Configure any additional variables required by your application and LLM provider.

**Important:**

* Never commit your real `.env` file or API keys to GitHub.
* Replace development credentials with strong, unique secrets.
* The hostnames `postgres` and `qdrant` are intended for communication between Docker Compose services.
* Ensure variable names match those defined in `app/core/config.py`.

### 3. Start the Application

Run the following command from the project root:

```bash
docker compose up -d --build
```

Check running services:

```bash
docker compose ps
```

View API logs:

```bash
docker compose logs -f api
```

### 4. Open the API Documentation

Once the application is running, open:

**Swagger UI:** http://localhost:8000/docs

**OpenAPI Schema:** http://localhost:8000/openapi.json

### 5. Check Application Health

Check liveness:

```bash
curl http://localhost:8000/health/live
```

Check readiness:

```bash
curl http://localhost:8000/health/ready
```

The readiness endpoint also checks the Qdrant collection setup.

---

## 🔌 API Endpoints

| Method | Endpoint        | Description                              |
| ------ | --------------- | ---------------------------------------- |
| GET    | `/health/live`  | Check whether the application is running |
| GET    | `/health/ready` | Check application readiness              |
| POST   | `/v1/documents` | Upload and index a PDF document          |
| POST   | `/v1/chat`      | Ask questions about available documents  |

### Authentication Headers

Protected endpoints use the following headers:

```http
x-api-key: YOUR_API_KEY
x-tenant-id: YOUR_TENANT_ID
```

The tenant identifier scopes document retrieval to the selected tenant.

---

## 💻 Usage Examples

### 1. Upload a PDF Document

```bash
curl -X POST "http://localhost:8000/v1/documents" \
  -H "x-api-key: YOUR_API_KEY" \
  -H "x-tenant-id: tenant-a" \
  -F "file=@document.pdf"
```

Example response:

```json
{
  "id": "2702652f-cb69-4b34-925e-514dc4837cb9",
  "filename": "document.pdf",
  "content_type": "application/pdf",
  "chunk_count": 3,
  "created_at": "2026-10-09T16:04:33.133115Z"
}
```

The response contains the document ID, filename, content type, chunk count, and creation timestamp.

### 2. Ask a Question

```bash
curl -X POST "http://localhost:8000/v1/chat" \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -H "x-tenant-id: tenant-a" \
  -d '{
    "question": "What is the name of the experiment?"
  }'
```

Example response:

```json
{
  "answer": "The experiment is described in the uploaded document.",
  "sources": [
    {
      "document_id": "2702652f-cb69-4b34-925e-514dc4837cb9",
      "filename": "document.pdf",
      "chunk_id": "0",
      "score": 0.82,
      "excerpt": "Relevant text retrieved from the document..."
    }
  ],
  "grounded": true,
  "request_id": "example-request-id"
}
```

*This is an illustrative response. Actual answers, scores, and excerpts depend on the uploaded document and retrieval results.*

### 3. Handle Insufficient Evidence

When retrieved evidence does not meet the configured threshold, the API returns an insufficient-information response.

Example:

```json
{
  "answer": "I could not find enough relevant information in the documents available to this tenant to answer reliably.",
  "sources": [],
  "grounded": false,
  "request_id": "example-request-id"
}
```

This behavior helps reduce unsupported, document-based answers.

---

## 🔐 Multi-Tenant Isolation

The platform scopes vector retrieval using a tenant ID stored in the vector payload.

Example workflow:

1. Tenant A uploads a document.
2. Tenant A asks a question about that document.
3. Tenant B submits the same question.
4. The retrieval filter prevents Tenant B from retrieving Tenant A's document through the tested retrieval path.

**Security consideration:** A tenant ID header alone does not establish a trusted tenant identity. For production, derive tenant identity from authenticated credentials or validated claims. Test isolation across upload, retrieval, database operations, and document-management endpoints.

---

## 🔧 Configuration

Important settings include:

| Setting              | Purpose                                             |
| -------------------- | --------------------------------------------------- |
| `APP_API_KEY`        | API authentication secret                           |
| `DATABASE_URL`       | PostgreSQL connection URL                           |
| `QDRANT_URL`         | Qdrant service URL                                  |
| `QDRANT_COLLECTION`  | Vector collection name                              |
| `MIN_EVIDENCE_SCORE` | Minimum retrieval score required to accept evidence |
| `TOP_K`              | Number of chunks retrieved, if configured           |

Refer to `app/core/config.py` and `.env.example` for the exact configuration supported by the application.

### Evidence Threshold

The evidence threshold determines whether retrieved chunks are considered relevant enough to answer a question.

* A higher threshold is more restrictive and may reject useful evidence.
* A lower threshold may accept less relevant evidence.
* The threshold should be evaluated against representative documents and questions.

A retrieval score is a relevance signal, not a guarantee of factual correctness.

---

## 🧪 Testing

The following manual checks have been performed during development:

| Test                                       | Result                                          |
| ------------------------------------------ | ----------------------------------------------- |
| PDF upload                                 | Successful                                      |
| Question answered by uploaded PDF          | Correct answer and source returned              |
| Unrelated question                         | Insufficient-information response returned      |
| Grounding flag for insufficient evidence   | Returned `false`                                |
| Source filtering for insufficient evidence | Returned an empty source list                   |
| Cross-tenant retrieval test                | Tenant B could not retrieve Tenant A's document |
| Liveness endpoint                          | Successful                                      |
| Readiness endpoint                         | Successful                                      |

Automated regression tests, load tests, and broader security tests should be added before production deployment.

---

## ⚠️ Error Handling

The API uses HTTP status codes to communicate request outcomes.

| Status Code                | Meaning                                    |
| -------------------------- | ------------------------------------------ |
| `200 OK`                   | Request processed successfully             |
| `400 Bad Request`          | Invalid upload or no extractable text      |
| `409 Conflict`             | Duplicate document detected for the tenant |
| `422 Unprocessable Entity` | Request validation failed                  |
| `503 Service Unavailable`  | Vector indexing failed                     |

Consult the endpoint implementation for the complete set of possible errors.

---

## 🚀 Production Considerations

Before deploying to production, consider the following improvements:

* Replace development credentials with strong secrets.
* Use authenticated tenant identity instead of trusting a raw tenant header.
* Add automated unit, integration, and tenant-isolation tests.
* Configure TLS and secure network access.
* Implement rate limiting and upload-size controls.
* Protect sensitive document content and metadata.
* Configure structured logging, metrics, tracing, and alerting.
* Implement PostgreSQL and Qdrant backup and recovery.
* Evaluate retrieval quality and answer faithfulness.
* Pin dependency versions and scan dependencies and container images.
* Use production-appropriate database credentials and connection settings.
* Review document deletion and vector cleanup behavior.
* Test concurrent requests and service failure scenarios.

The application has been demonstrated locally using Docker Compose. Additional security, reliability, and operational validation is required before production deployment.

---

## 🔮 Future Improvements

* Support additional document formats such as DOCX and TXT.
* Implement hybrid keyword and semantic search.
* Add reranking for improved retrieval relevance.
* Support streaming responses.
* Add conversation history and session management.
* Implement document deletion and re-indexing.
* Add automated RAG evaluation.
* Introduce role-based access control.
* Add metrics and distributed tracing.
* Implement CI/CD pipelines.
* Build a web frontend for document management and chat.

---

## 📚 Learning Outcomes

This project demonstrates practical experience with:

* Building asynchronous REST APIs using FastAPI.
* Designing document-ingestion pipelines.
* Generating and storing vector embeddings.
* Implementing semantic search with Qdrant.
* Orchestrating workflows using LangGraph.
* Integrating LLMs into a RAG pipeline.
* Managing relational databases using SQLAlchemy and Alembic.
* Implementing tenant-scoped retrieval.
* Containerizing applications using Docker Compose.
* Handling insufficient evidence in retrieval-based question answering.

---

## 📄 License
This project is licensed under the terms of the license specified in the [`LICENSE`](LICENSE) file. See the file for details.

---

**GenAI Production Platform — A Generative AI engineering project focused on document intelligence, Retrieval-Augmented Generation, and multi-tenant API design.**
