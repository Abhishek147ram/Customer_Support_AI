# Customer Support AI

## Project Overview

Customer Support AI is an AI-powered support automation system designed to streamline ticket processing, improve agent productivity, and automate customer service workflows.

The system leverages locally hosted LLMs through Ollama to perform intelligent ticket analysis, response generation, prioritization, and escalation recommendations.

The architecture is designed to be modular, scalable, and production-oriented while remaining lightweight for local deployment and experimentation.

---

# Features

### Automated Ticket Classification

Automatically categorizes incoming tickets into predefined categories such as:

* Technical Issues
* Billing Queries
* Account Problems
* Product Questions
* Complaints

### AI-Powered Response Suggestions

Generates draft responses to reduce manual support workload.

### Priority Prediction & Escalation

Automatically identifies urgent cases and recommends escalation when required.

### Sentiment & Context Analysis

Analyzes ticket context to assist support agents with decision making.

### Secure API Layer

FastAPI-based REST APIs with validation, authentication support, and structured error handling.

### Scalable Deployment

Containerized deployment using Docker for portability and easier scaling.

### Testing Coverage

Includes unit tests, API tests, validation tests, and workflow testing.

---

# Technology Stack

| Layer            | Technology             |
| ---------------- | ---------------------- |
| Backend          | FastAPI                |
| Database         | SQLite + SQLAlchemy    |
| AI / LLM         | Ollama (Local Models)  |
| Validation       | Pydantic               |
| Migrations       | Alembic                |
| Containerization | Docker, Docker Compose |
| Testing          | Pytest                 |

---

# Setup & Installation

## Prerequisites

* Python 3.9+
* Docker & Docker Compose
* Ollama installed locally

---

## Clone Repository

```bash
git clone <repository-url>
cd customer_support_AI
```

---

## Configure Environment Variables

Create environment configuration:

```bash
cp .env.example .env
```

Update values:

```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
DATABASE_URL=sqlite+aiosqlite:///./data/support_tickets.db
```

---

## Start Services

```bash
docker-compose up --build
```

---

## Database Migration

```bash
alembic upgrade head
```

---

# Usage

Run locally:

```bash
uv run uvicorn app.main:app --reload
```

Application endpoints:

Swagger UI:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

Health Check:

```text
http://localhost:8000/health
```

---

# Project Structure

```text
customer_support_AI/
│
├── app/
│   ├── config/
│   ├── database/
│   ├── dependencies/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   └── main.py
│
├── data/
├── docs/
├── tests/
├── alembic/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
└── README.md
```

---

# Documentation

Project documentation includes:

* Architecture documentation
* Production considerations
* Screenshots
* Demo materials
* Testing artifacts
* Workflow documentation

---

# Future Improvements

* Add vector database integration
* Multi-model workflows
* Advanced analytics dashboard
* Expanded monitoring and observability
* Production database migration

---

# License

MIT License

```
```
