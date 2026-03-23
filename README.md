# Policy Management API

**A production-grade insurance policy management system** designed specifically for Canadian insurers such as Sun Life, Manulife, and Definity.

## Project Highlights

- High-performance asynchronous backend built with **FastAPI + PostgreSQL**
- **JWT Authentication** with role-based access control (Admin / Underwriter)
- Full **CRUD operations** on policies + **bulk import** supporting 100,000+ records (CSV/JSON)
- Built-in **insurance business rule validation**: anti-fraud engine and automatic OSFI compliance flag generation
- **Docker one-click deployment**
- Designed to align with Canadian insurance regulatory requirements (OSFI)

## Tech Stack
- **Backend**: FastAPI, Uvicorn, SQLAlchemy 2.0, Alembic
- **Database**: PostgreSQL (asynchronous)
- **Authentication**: JWT (PyJWT + bcrypt)
- **Validation & Schema**: Pydantic v2
- **Deployment**: Docker + docker-compose
- **Data Processing**: Pandas (for bulk import)

---

## Quick Start

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd policy-management-api

# 2. Start the services
docker-compose up --build -d

# 3. Open Swagger documentation
http://localhost:8000/docs
```

## Environment Variables
.env

## Main API Features
### Authentication

- POST /api/v1/auth/register — User registration
- POST /api/v1/auth/login — User login

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

## License
- MIT License