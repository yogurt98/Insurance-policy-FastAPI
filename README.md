# Policy Management API

**A production-grade insurance policy management system** designed specifically for Canadian insurers such as Sun Life, Manulife, and Definity.

## Project Highlights

- High-performance asynchronous backend built with **FastAPI + PostgreSQL**
- **JWT Authentication** with role-based access control (Admin / Underwriter)
- Full **CRUD operations** on policies + **bulk import** supporting 100,000+ records (CSV/JSON)
- Built-in **insurance business rule validation**: anti-fraud engine and automatic OSFI compliance flag generation
- **Docker one-click deployment**
- Structured logging, correlation ID, rate limiting, Redis caching, Celery event-driven tasks

### Tech Stack
- **Framework**: FastAPI, Uvicorn
- **Database**: PostgreSQL (async via SQLAlchemy 2.0 + Alembic)
- **Auth**: JWT (PyJWT + bcrypt)
- **Validation**: Pydantic v2
- **Data Processing**: Pandas (bulk import)
- **Caching**: Redis + fastapi-cache
- **Async Tasks**: Celery + Redis (event-driven notifications)
- **Testing**: pytest
- **Deployment**: Docker, Render (demo)

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yogurt98/Insurance-policy-FastAPI.git
cd project-FastAPI

# 2. Start the services
docker-compose up --build -d

# 3. Open Swagger documentation
http://localhost:8000/docs
```

## Environment Variables
.env

## Live Demo (Render)
A live demo is deployed on Render (free tier):
🔗 https://insurance-policy-fastapi.onrender.com/docs

- Swagger UI: https://insurance-policy-fastapi.onrender.com/docs
- Note: Render free tier may sleep after inactivity (first request ~30s delay)

(If the demo link is down, feel free to deploy your own fork using the Render button below or follow the guide in the Deployment section.)




## Main API Features
### Authentication

- POST /api/v1/auth/register — User registration
- POST /api/v1/auth/login — User login and get JWT

### Policy Management

- POST /api/v1/policies/ — Create policy (with anti-fraud validation)
- GET /api/v1/policies/ — List policies
- GET /api/v1/policies/{id} — Get single policy
- PUT /api/v1/policies/{id} — Update policy
- DELETE /api/v1/policies/{id} — Delete policy (Admin only)

### Bulk Import (Core Feature)

- POST /api/v1/policies/bulk-upload — Upload large CSV/JSON files (supports 100,000+ records)

### Insurance Business Features

- Anti-fraud rule engine: automatic flagging (flag / review) based on risk score and abnormal premium
- OSFI compliance: auto-generation of OSFI-YYYY-XXXXXX identifier
- Precise premium handling: stored as Numeric(precision=2)
- Role-based access: Underwriter can create/view, Admin can delete



## Postman Collection
- A complete Postman collection is provided in the project root: postman_collection.json.
- Import it directly into Postman to test all endpoints.

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