# 🛡️ Insurance Policy Management API

![CI Pipeline](https://github.com/yogurt98/Insurance-policy-FastAPI/actions/workflows/ci.yml/badge.svg)

![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-00a393.svg)

![AWS EC2](https://img.shields.io/badge/AWS-EC2-FF9900?logo=amazonaws&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-IaC-623CE4?logo=terraform&logoColor=white)

![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-Orchestration-2496ED?logo=docker&logoColor=white)

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)
![Redis](https://img.shields.io/badge/Redis-7-dc382d.svg)

![Celery](https://img.shields.io/badge/Celery-Task_Queue-37814A?logo=celery&logoColor=white)

![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI/CD-2088FF?logo=githubactions&logoColor=white)

**A production-grade insurance policy management system** designed specifically for Canadian insurers such as Sun Life, Manulife, and Definity.

## Project Highlights

- **Cloud-Native Deployment:** Infrastructure provisioned with Terraform and deployed on AWS EC2 using Docker Compose.
- **High-Performance Async Backend:** Built with FastAPI, Uvicorn, and async SQLAlchemy 2.0 for scalable API performance.
- **Enterprise Security:** JWT Authentication with Role-Based Access Control (Admin vs. Underwriter).
- **Insurance Business Logic:** Integrated anti-fraud validation, OSFI compliance tracking, and policy lifecycle management.
- **High-Volume Data Processing:** Supports 100,000+ policy records through bulk CSV/JSON ingestion with Pandas and Celery background tasks.
- **Production-Ready Engineering:** GitHub Actions CI/CD, structured logging, Redis caching, and containerized deployment with Docker.
---
## System Architecture
```mermaid
flowchart TD
    Dev["Developer / Local Machine"]
    GitHub["GitHub Repository"]
    TF["Terraform IaC"]

    subgraph AWS["AWS Cloud"]
        SG["Security Group<br/>Inbound: 22, 80, 8000"]
        EC2["Amazon EC2 Instance<br/>Amazon Linux 2023"]

        subgraph Docker["Docker Compose Runtime"]
            API["FastAPI Application<br/>Swagger UI / REST API"]
            DB[("PostgreSQL<br/>Policy Database")]
            Redis[("Redis<br/>Cache & Token Blacklist")]
            Celery["Celery Worker<br/>Background Tasks"]
        end
    end

    User["User / API Client"]

    Dev -->|"terraform init / apply"| TF
    TF -->|"provisions"| SG
    TF -->|"provisions"| EC2
    EC2 -->|"git clone"| GitHub
    EC2 -->|"docker compose up -d --build"| Docker

    User -->|"HTTP :8000<br/>/docs & API requests"| SG
    SG --> EC2
    EC2 --> API

    API <-->|"async SQLAlchemy"| DB
    API <-->|"cache / blacklist"| Redis
    API -->|"send background jobs"| Celery
    Celery <-->|"read / write tasks"| DB
    Celery <-->|"broker / result backend"| Redis

    classDef dev fill:#2f3542,stroke:#ffffff,color:#ffffff
    classDef cloud fill:#ff9900,stroke:#ffffff,color:#ffffff
    classDef infra fill:#57606f,stroke:#ffffff,color:#ffffff
    classDef app fill:#00a393,stroke:#ffffff,color:#ffffff
    classDef db fill:#336791,stroke:#ffffff,color:#ffffff
    classDef cache fill:#dc382d,stroke:#ffffff,color:#ffffff
    classDef worker fill:#37814a,stroke:#ffffff,color:#ffffff
    classDef user fill:#1e90ff,stroke:#ffffff,color:#ffffff

    class Dev,GitHub dev
    class TF,SG infra
    class AWS,EC2 cloud
    class API app
    class DB db
    class Redis cache
    class Celery worker
    class User user
```
---

## Tech Stack
- **Framework**: FastAPI, Uvicorn
- **Database**: PostgreSQL (async via SQLAlchemy 2.0 + Alembic)
- **Auth**: JWT (PyJWT + bcrypt)
- **Validation**: Pydantic v2
- **Data Processing**: Pandas (bulk import)
- **Caching**: Redis + fastapi-cache
- **Async Tasks**: Celery + Redis (event-driven notifications)
- **Testing**: pytest
- **Deployment**:
  Docker
  Docker Compose
  Terraform
  AWS EC2
  Render

---

## Live Demo (Render)
A live demo is deployed on Render (free tier):
🔗 https://insurance-policy-fastapi.onrender.com/docs

- Swagger UI: https://insurance-policy-fastapi.onrender.com/docs
- Note: Render free tier may sleep after inactivity (first request ~30s delay)

(If the demo link is down, feel free to deploy your own fork using the Render button below or follow the guide in the Deployment section.)
> **Note**: This is hosted on a free Render instance. It spins down after 15 minutes of inactivity. **The first request may take 30–60 seconds to wake up the server.**

![img.png](img.png)

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yogurt98/Insurance-policy-FastAPI.git
cd project-FastAPI

# 2. Environment Setup
# Copy the example environment file and configure your credentials:
cp .env.example .env
# Important: Update SECRET_KEY and POSTGRES passwords if needed


# 3. Start the services with Docker
docker-compose up --build -d

# 3. Open Swagger documentation
http://localhost:8000/docs
```

---
## Main API Features
###  Authentication
- POST /api/v1/auth/register — Register a new user (Roles: Admin/Underwriter).

- POST /api/v1/auth/login — Authenticate and obtain a JWT access token.

- POST /api/v1/auth/logout — Secure logout (Adds token to a Redis-backed blacklist).

###  Policy Management
- POST /api/v1/policies/ — Create a policy (Triggers anti-fraud & OSFI checks).

- GET /api/v1/policies/ — Retrieve paginated policies (Results cached in Redis).

- GET /api/v1/policies/{id} — Get single policy details.

- PUT /api/v1/policies/{id} — Update an existing policy.

- DELETE /api/v1/policies/{id} — Delete a policy (Restricted to Admin role).

###  Bulk Operations & Business Logic
- POST /api/v1/policies/bulk-upload — Upload CSV/JSON. Tasks are delegated to Celery for background processing, ensuring the API remains responsive.

- Anti-Fraud Engine: Automatically flags policies for review based on risk_score and premium thresholds.

- Regulatory Compliance: Auto-generates unique OSFI-YYYY-XXXXXX identifiers for tracking.

- Financial Accuracy: Utilizes Numeric(precision=2) for all premium calculations to prevent floating-point errors.

- Celery Task Execution Screenshot Placeholder

### Insurance Business Features

- Anti-fraud rule engine: automatic flagging (flag / review) based on risk score and abnormal premium
- OSFI compliance: auto-generation of OSFI-YYYY-XXXXXX identifier
- Precise premium handling: stored as Numeric(precision=2)
- Role-based access: Underwriter can create/view, Admin can delete
---
##  Testing & CI/CD
The project includes a comprehensive suite of unit and integration tests covering CRUD operations, bulk uploads, anti-fraud validation, and JWT blacklisting.

### Run tests locally inside the Docker container:

```docker-compose exec api pytest app/tests/ -v```

### Continuous Integration:
A GitHub Actions workflow is triggered on every push and pull request to the **main** branch. It provisions a PostgreSQL & Redis service, lints the code with **flake8**, and executes the **pytest** suite to ensure no regressions.

![img_2.png](img_2.png)

---


## Postman Collection
- A complete Postman collection is provided in the project root: postman_collection.json.
- Import it directly into Postman to test all endpoints.
![img_1.png](img_1.png)
---

## AWS Deployment with Terraform

This project includes Infrastructure as Code (IaC) deployment using Terraform on AWS.

### Provisioned AWS Resources

- Amazon EC2
- Security Group
- Docker Runtime
- Docker Compose Deployment

### Deployed Services

- FastAPI Application
- PostgreSQL Database
- Redis Cache
- Celery Worker

### Architecture

```text
Terraform
    │
    ▼
AWS EC2
    │
    ├── FastAPI API
    ├── PostgreSQL
    ├── Redis
    └── Celery
```

### Deployment

```bash
cd terraform

terraform init

terraform apply
```

### Access API Documentation

```text
http://<EC2_PUBLIC_IP>:8000/docs
```

### Cleanup

```bash
terraform destroy
```

### Example Deployment

The application has been successfully deployed on AWS EC2 using Terraform and Docker Compose.

Swagger UI:
![aws-swagger-ui.png](aws-swagger-ui.png)
## Deployment Guide (Render Free Tier)
1. Fork this repo to your GitHub 
2. Go to https://render.com → New → Web Service 
3. Connect your forked GitHub repo 
4. Choose Docker runtime 
5. Set environment variables (from .env.example)
- DATABASE_URL: Use Render's PostgreSQL addon (free tier available). Use **postgresql+asyncpg://** not **postgres://**
- SECRET_KEY: Generate a strong key

6. Deploy → Wait 5–10 minutes
7. Access Swagger at https://your-app.onrender.com/docs

- Note: Free tier sleeps after 15 minutes inactivity (first request slow).


## License
- MIT License