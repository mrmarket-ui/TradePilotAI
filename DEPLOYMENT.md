# Deployment Guide

## Requirements

- Python 3.14+
- PostgreSQL (Production)
- FastAPI
- Uvicorn
- Nginx (Optional)
- Docker (Optional)

---

## Install

```bash
pip install -r requirements.txt
```

---

## Environment Variables

```
SECRET_KEY=
OPENAI_API_KEY=
OPENAI_MODEL=
DATABASE_URL=
```

---

## Run

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Production

Recommended platforms:

- Railway
- Render
- Azure
- AWS
- DigitalOcean
- VPS

---

## Security

- HTTPS
- JWT Authentication
- Environment Variables
- SQLAlchemy ORM
- Request Validation