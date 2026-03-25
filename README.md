# Snippet Vault

A code snippet vault API built with Django and Django REST Framework.

## Setup

```bash
cp .env.example .env
# Edit .env — set a strong SECRET_KEY and POSTGRES_PASSWORD
```

## Running locally

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

## Apply migrations

```bash
docker-compose exec api python manage.py migrate
```

## Create a superuser

```bash
docker-compose exec api python manage.py createsuperuser
```

## Run tests

```bash
docker-compose exec api pytest
```

## Health check

```bash
curl http://localhost:8000/health/
```

## Error response format

All API errors return a consistent JSON envelope:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Validation error",
    "details": {
      "field_name": ["This field is required."]
    }
  }
}
```
