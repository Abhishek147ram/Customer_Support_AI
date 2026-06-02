# 🤖 Customer Support AI

## 📌 Project Overview

Customer Support AI is an AI-powered support automation system designed to streamline ticket processing, improve agent productivity, and automate customer service workflows.

The system leverages locally hosted LLMs through Ollama to perform intelligent ticket analysis, response generation, prioritization, and escalation recommendations.

The architecture is modular, scalable, and production-oriented while remaining lightweight for local deployment and experimentation.

---

## ✨ Features

### 🧾 Automated Ticket Classification
Automatically categorizes incoming tickets into:
- Technical Issues
- Billing Queries
- Account Problems
- Product Questions
- Complaints

### 💬 AI-Powered Response Suggestions
Generates intelligent draft responses to reduce manual support workload.

### 🚨 Priority Prediction & Escalation
Identifies urgent cases and recommends escalation when required.

### 📊 Sentiment & Context Analysis
Analyzes customer sentiment and context to assist decision-making.

### 🔐 Secure API Layer
FastAPI-based REST APIs with validation, structured error handling, and scalable design.

### 🐳 Scalable Deployment
Containerized using Docker and Docker Compose for portability and scalability.

### 🧪 Testing Coverage
Includes unit tests, API tests, validation tests, and workflow testing.

---

## ⚙️ Technology Stack

| Layer            | Technology |
|------------------|------------|
| Backend          | FastAPI |
| Database         | SQLite + SQLAlchemy |
| AI / LLM         | Ollama (Local Models) |
| Validation       | Pydantic |
| Migrations       | Alembic |
| Containerization | Docker, Docker Compose |
| Testing          | Pytest |
| Bonus Points     | AI agents (ticket automation components), real API integrations (LLM services), cost optimization analysis (local inference strategy), production deployment thinking (Dockerized scalable architecture), workflow automation design |

---

## ⚙️ Configure Environment Variables

Create a `.env` file in the project root:

---

## 📄 Example `.env`

```env id="env_block"
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
DATABASE_URL=sqlite+aiosqlite:///./data/support_tickets.db
````

---

## 🐳 Run with Docker

```bash id="docker_run"
docker-compose up --build
```

---

## 🗄️ Database Migration

```bash id="db_migrate"
alembic upgrade head
```

---

## ▶️ Usage

### Run locally:

```bash id="run_local"
uv run uvicorn app.main:app --reload
```

---

## 🔗 API Endpoints

* Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
* Health Check: [http://localhost:8000/health](http://localhost:8000/health)

---

## 📁 Project Structure

```text id="structure"
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
├── .env.example
└── README.md
```

---

## 📚 Documentation

* Architecture design
* Production deployment guide
* Testing reports
* Workflow diagrams
* Audit reports
* Demo materials

---

## 🚀 Future Improvements

* Vector database integration (FAISS / Chroma)
* Multi-agent AI workflows
* Advanced analytics dashboard
* Observability (Prometheus / Grafana)
* PostgreSQL migration for production scaling

---

## 📜 License

MIT License

```

---

If you want next upgrade, I can turn this into:
- 🔥 **:contentReference[oaicite:0]{index=0}**
- 📊 **:contentReference[oaicite:1]{index=1}**
- 💼 **:contentReference[oaicite:2]{index=2}**
- 🚀 **:contentReference[oaicite:3]{index=3}**

Just tell me 👍
```
