# GenAI Production Platform

### Multi-Tenant Agentic RAG API

![CI](https://github.com/JRM1-star/Genai-Production-Platform/actions/workflows/ci.yml/badge.svg)


A Generative AI platform that allows users to upload PDF documents and ask questions about their contents using Retrieval-Augmented Generation (RAG).

The platform combines semantic search, vector embeddings, document retrieval, and LLM-powered answering to generate context-aware responses with source attribution.

**Built with FastAPI, LangGraph, PostgreSQL, Qdrant, Groq, and Docker Compose.**

---

## 🚀 Key Features

* **PDF Document Ingestion:** Upload PDF documents through a REST API.
* **Text Extraction and Chunking:** Extract text and divide it into smaller chunks.
* **Semantic Search:** Generate embeddings and retrieve relevant document chunks.
* **Retrieval-Augmented Generation:** Generate answers using retrieved document context.
* **Multi-Tenant Isolation:** Filter vector retrieval by tenant ID.
* **Evidence Evaluation:** Use a configurable relevance threshold to assess retrieved evidence.
* **Source Attribution:** Return source documents, chunk IDs, relevance scores, and text excerpts.
* **API Authentication:** Protect endpoints using API key authentication.
* **PostgreSQL Persistence:** Store document metadata using SQLAlchemy and Alembic.
* **Vector Database:** Store and search embeddings using Qdrant.
* **Structured Logging:** Record request IDs, response status codes, and request durations.
* **Health Checks:** Monitor application liveness and readiness.
* **Dockerized Deployment:** Run application services using Docker Compose.

---

## 🏗️ System Architecture

```mermaid
flowchart TB
    U["Client / API Consumer"]

    subgraph API["API Layer — FastAPI"]
        AUTH["API Key Authentication"]
        DOC["Document Upload API"]
        CHAT["Chat API"]
    end

    subgraph INGEST["Document Ingestion"]
        PARSE["PDF Text Extraction"]
        CHUNK["Text Chunking"]
        EMBED["Embedding Generation"]
        UPSERT["Store Vectors"]
        METADATA["Store Document Metadata"]
    end

    subgraph RAG["RAG Workflow — LangGraph"]
        RETRIEVE["Retrieve Relevant Chunks"]
        EVAL["Evaluate Evidence"]
        ROUTE{"Sufficient Evidence?"}
        GENERATE["Generate Answer"]
        FALLBACK["Insufficient-Evidence Response"]
        RESPONSE["Answer, Sources, and Grounded Status"]
    end

    subgraph STORAGE["Data Layer"]
        QDRANT[("Qdrant")]
        POSTGRES[("PostgreSQL")]
    end

    LLM["Groq LLM"]

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
```

---

## 🛠️ Technology Stack

| Technology     | Purpose                              |
| -------------- | ------------------------------------ |
| Python 3.12    | Backend development                  |
| FastAPI        | REST API framework                   |
| LangGraph      | RAG workflow orchestration           |
| Groq API       | LLM inference                        |
| Qdrant         | Vector storage and similarity search |
| FastEmbed      | Embedding generation                 |
| PostgreSQL     | Document metadata storage            |
| SQLAlchemy     | Database access and ORM              |
| Alembic        | Database migrations                  |
| Pydantic       | Data validation and settings         |
| Structlog      | Structured logging                   |
| Docker         | Containerization                     |
| Docker Compose | Manage application services          |
| Swagger UI     | Interactive API documentation        |

---

## 🔄 RAG Workflow

1. **Document Upload:** Upload a PDF through the API.
2. **Text Extraction:** Extract readable text from the PDF.
3. **Chunking:** Divide extracted text into smaller chunks.
4. **Embedding Generation:** Convert chunks into vector embeddings.
5. **Vector Storage:** Store embeddings and associated metadata in Qdrant.
6. **Question Processing:** Submit a question to the chat endpoint.
7. **Semantic Retrieval:** Retrieve relevant chunks using vector similarity search.
8. **Evidence Evaluation:** Compare retrieval scores against the configured threshold.
9. **Answer Generation:** Generate an answer using retrieved context when sufficient evidence is available.
10. **Fallback Handling:** Return an insufficient-information response when evidence is insufficient.
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
├── tests/
│
├── .env.example
├── .gitignore
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

*The tree illustrates the expected structure. Adjust it if your actual repository differs.*

---

## ⚙️ Getting Started

### Prerequisites

Install or obtain the following:

* Git
* Docker Desktop with Docker Compose
* A Groq API key
* An internet connection for pulling Docker images and downloading dependencies

Python 3.12 is required if you intend to run the application outside Docker.

### 1. Clone the Repository

```bash
git clone https://github.com/JRM1-star/Genai-Production-Platform.git
cd Genai-Production-Platform
```

Make sure the cloned directory is the project root containing `docker-compose.yml`.

### 2. Configure Environment Variables

Create a `.env` file in the project root using `.env.example` as a template.

On PowerShell:

```powershell
Copy-Item .env.example .env
```

Edit `.env` and configure the required values:

```dotenv
APP_ENV=development
APP_API_KEY=replace-with-a-strong-secret
LOG_LEVEL=INFO

GROQ_API_KEY=your-groq-api-key
GROQ_MODEL=openai/gpt-oss-120b

POSTGRES_PASSWORD=app
DATABASE_URL=postgresql+asyncpg://app:app@postgres:5432/genai

QDRANT_URL=http://qdrant:6333
QDRANT_API_KEY=
QDRANT_COLLECTION=knowledge_chunks

EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
MAX_UPLOAD_MB=10
TOP_K=6
MIN_EVIDENCE_SCORE=0.65
REQUEST_TIMEOUT_SECONDS=45

CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

These are development examples. Use appropriate values for your local configuration and ensure they match the settings supported by `app/core/config.py`.

**Important security notes:**

* Never commit your actual `.env` file or API keys to GitHub.
* Replace placeholder secrets before using the application.
* The example PostgreSQL password is for local development only.
* The hostnames `postgres` and `qdrant` are intended for communication between Docker Compose services.
* Production deployments must use strong credentials and appropriately restricted network access.

### 3. Start the Application

From the project root, run:

```bash
docker compose up -d --build
```

Check the service status:

```bash
docker compose ps
```

View application logs:

```bash
docker compose logs -f api
```

The API container runs database migrations before starting Uvicorn.

### 4. Open API Documentation

Once the application has started, open:

* **Swagger UI:** http://localhost:8000/docs
* **OpenAPI Schema:** http://localhost:8000/openapi.json

### 5. Check Application Health

Liveness endpoint:

```bash
curl http://localhost:8000/health/live
```

Readiness endpoint:

```bash
curl http://localhost:8000/health/ready
```

The readiness endpoint initializes or checks the Qdrant collection. It should not be treated as a comprehensive health check of every external dependency unless those checks are explicitly implemented.

---

## 🔌 API Endpoints

| Method | Endpoint        | Description                                             |
| ------ | --------------- | ------------------------------------------------------- |
| GET    | `/health/live`  | Check whether the application is running                |
| GET    | `/health/ready` | Check application readiness and Qdrant collection setup |
| POST   | `/v1/documents` | Upload and index a PDF document                         |
| POST   | `/v1/chat`      | Ask questions about documents available to the tenant   |

### Authentication Headers

Protected endpoints require:

```http
x-api-key: YOUR_API_KEY
x-tenant-id: YOUR_TENANT_ID
```

The API key authenticates the request. The tenant ID scopes document retrieval.

**Production consideration:** A tenant ID supplied directly in a header should not, by itself, be considered proof of tenant identity. Production systems should derive tenant identity from trusted authentication credentials or validated claims.

---

## 💻 Usage Examples

### 1. Upload a PDF

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

This example is illustrative. The actual response depends on the uploaded document.

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

The answer, relevance scores, excerpts, and request ID will vary for each request.

### 3. Handle Insufficient Evidence

When the retrieval workflow determines that the evidence is insufficient, the application can return an answer indicating that the available documents do not provide enough information.

Illustrative response:

```json
{
  "answer": "I could not find enough relevant information in the documents available to this tenant to answer reliably.",
  "sources": [],
  "grounded": false,
  "request_id": "example-request-id"
}
```

The exact fallback message depends on the workflow implementation.

---

## 🔐 Multi-Tenant Isolation

The application scopes vector retrieval using a tenant identifier stored in the Qdrant payload.

Example workflow:

1. Tenant A uploads a document.
2. Tenant A asks a question about that document.
3. Tenant B submits the same question.
4. The tenant filter prevents Tenant B from retrieving Tenant A's document through the tested retrieval path.

Tenant isolation must be consistently enforced across all data-access paths, including document uploads, retrieval, database queries, and any future document-management endpoints.

For production, use authenticated tenant identity and verify isolation through automated integration tests.

---

## 🔧 Configuration

Important settings include:

| Setting                   | Purpose                                        |
| ------------------------- | ---------------------------------------------- |
| `APP_ENV`                 | Application environment                        |
| `APP_API_KEY`             | API authentication secret                      |
| `GROQ_API_KEY`            | Groq API credential                            |
| `GROQ_MODEL`              | Model used for answer generation               |
| `DATABASE_URL`            | PostgreSQL connection URL                      |
| `POSTGRES_PASSWORD`       | PostgreSQL password used by Docker Compose     |
| `QDRANT_URL`              | Qdrant service URL                             |
| `QDRANT_API_KEY`          | Optional Qdrant API key                        |
| `QDRANT_COLLECTION`       | Vector collection name                         |
| `EMBEDDING_MODEL`         | Embedding model identifier                     |
| `MAX_UPLOAD_MB`           | Maximum allowed upload size                    |
| `TOP_K`                   | Number of chunks retrieved                     |
| `MIN_EVIDENCE_SCORE`      | Minimum retrieval score for accepting evidence |
| `REQUEST_TIMEOUT_SECONDS` | Configured request timeout                     |
| `CORS_ORIGINS`            | Allowed browser origins                        |
| `LOG_LEVEL`               | Logging verbosity                              |

Refer to `app/core/config.py` and `.env.example` for the settings supported by the application.

### Evidence Threshold

The evidence threshold controls how restrictive the retrieval workflow is when deciding whether retrieved chunks provide enough evidence to answer a question.

* A higher threshold may reject useful evidence.
* A lower threshold may accept less relevant evidence.
* The threshold should be evaluated against representative documents and questions.

A retrieval score is a relevance signal, not a guarantee of factual correctness.

---

## 🧪 Testing and Validation

During development, the following checks have been reported:

| Check                                | Result                             |
| ------------------------------------ | ---------------------------------- |
| PDF upload                           | Successful                         |
| Question answered using uploaded PDF | Answer and sources returned        |
| Missing tenant header                | Rejected                           |
| Invalid API key                      | Rejected                           |
| Cross-tenant retrieval               | Tenant-specific retrieval observed |
| Liveness endpoint                    | Successful                         |
| Readiness endpoint                   | Successful                         |
| Ruff linting                         | All checks passed                  |

These are development observations, not a substitute for a reproducible automated test suite.

Automated regression tests, load tests, and broader security tests should be added before production deployment.

---

## ⚠️ Error Handling

The API uses HTTP status codes to communicate request outcomes.

| Status Code                | Meaning                                                                             |
| -------------------------- | ----------------------------------------------------------------------------------- |
| `200 OK`                   | Request processed successfully                                                      |
| `400 Bad Request`          | Invalid upload or no extractable text                                               |
| `401 Unauthorized`         | Invalid API key                                                                     |
| `409 Conflict`             | Duplicate document detected for the tenant                                          |
| `413 Payload Too Large`    | Upload exceeds the configured size limit, when validation identifies it accordingly |
| `422 Unprocessable Entity` | Request validation failed                                                           |
| `503 Service Unavailable`  | Vector indexing failed or a service is unavailable                                  |

The exact status codes depend on the endpoint implementation and error condition.

---

## 🚀 Production Considerations

Before deploying to production:

* Replace development credentials with strong, unique secrets.
* Use authenticated tenant identity rather than trusting a raw tenant header.
* Add automated unit, integration, and tenant-isolation tests.
* Configure TLS and secure network access.
* Implement rate limiting and upload-size controls.
* Protect sensitive document content and metadata.
* Configure structured logging, metrics, tracing, and alerting.
* Implement PostgreSQL and Qdrant backup and recovery.
* Evaluate retrieval quality and answer faithfulness.
* Pin dependency and container image versions.
* Scan dependencies and container images for vulnerabilities.
* Use production-appropriate database credentials and connection settings.
* Review document deletion and vector cleanup behavior.
* Test concurrent requests and service failure scenarios.
* Review API-key rotation and secret-management procedures.

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

This project is licensed under the terms specified in the [`LICENSE`](LICENSE) file. See that file for details.

---
**GenAI Production Platform — A Generative AI engineering project focused on document intelligence, Retrieval-Augmented Generation, and multi-tenant API design.**
