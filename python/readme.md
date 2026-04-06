# FastAPI — Complete Learning Guide

> Data validation · REST APIs · PostgreSQL · Production patterns
> Based on building **PaySync** — a multi-tenant payment gateway

---

## Table of Contents

1. [What is FastAPI?](#1-what-is-fastapi)
2. [Uvicorn — the engine](#2-uvicorn--the-engine)
3. [Your first FastAPI app](#3-your-first-fastapi-app)
4. [API Methods](#4-api-methods)
5. [Pydantic — data validation](#5-pydantic--data-validation)
6. [Project structure](#6-project-structure)
7. [SQLAlchemy — ORM](#7-sqlalchemy--orm)
8. [psycopg2 — the DB driver](#8-psycopg2--the-db-driver)
9. [The full request lifecycle](#9-the-full-request-lifecycle)
10. [Layer-by-layer story](#10-layer-by-layer-story)
11. [OpenAPI — auto docs](#11-openapi--auto-docs)
12. [Concurrency vs parallelism](#12-concurrency-vs-parallelism)
13. [PaySync creation flow](#13-paysync-creation-flow)

---

## 1. What is FastAPI?

FastAPI is a modern Python web framework for building REST APIs. It is built on top of **Starlette** (async web toolkit) and **Pydantic** (data validation).

**Why FastAPI for payments / fintech?**

| Feature | What it gives you |
|---|---|
| Pydantic validation | Reject malformed requests before they touch your DB |
| Auto docs (Swagger) | Every endpoint documented automatically |
| Type hints | IDE autocomplete + runtime safety |
| Async support | Handle thousands of concurrent requests |
| Dependency injection | Clean auth, DB sessions, rate limiting |

**FastAPI request flow:**

```
Client (Postman / Browser / Mobile)
        ↓
  Route handler  (@app.get, @app.post ...)
        ↓
  Pydantic model  (validates + parses JSON → Python object)
        ↓
  Business logic  (service layer)
        ↓
  Response        (Python object → JSON)
```

---

## 2. Uvicorn — the engine

FastAPI is the **code**. Uvicorn is the **engine that runs it**.

```
Browser → Uvicorn → FastAPI → Response
```

| Thing | Role |
|---|---|
| FastAPI | Your application logic |
| Uvicorn | ASGI server — handles HTTP, WebSockets, async |
| Gunicorn | Process manager — runs multiple Uvicorn workers in production |

### Running the server

```bash
# Development — hot reload on every file save
uvicorn main:app --reload

# What each part means:
# main     → the filename (main.py)
# app      → the FastAPI() instance inside that file
# --reload → restart server automatically when code changes
```

### Production (multiple workers)

```bash
gunicorn app.main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 4 \
  --bind 0.0.0.0:8000
```

> **Rule of thumb:** workers = (2 × CPU cores) + 1. A 2-core server → 5 workers.

---

## 3. Your first FastAPI app

```python
from fastapi import FastAPI

app = FastAPI(
    title="PaySync API",
    description="Multi-tenant payment gateway",
    version="1.0.0",
)

@app.get("/")
def root():
    return {"message": "Hello, PaySync"}

@app.get("/health")
def health():
    return {"status": "healthy"}
```

After running `uvicorn main:app --reload`:

- **`http://localhost:8000/`** → your route
- **`http://localhost:8000/docs`** → Swagger UI (auto-generated, interactive)
- **`http://localhost:8000/redoc`** → ReDoc (alternative docs)
- **`http://localhost:8000/openapi.json`** → raw OpenAPI schema

---

## 4. API Methods

```python
@app.get("/transactions")          # Read — list or fetch
@app.post("/transactions")         # Create — new resource
@app.put("/transactions/{id}")     # Replace — full update
@app.patch("/transactions/{id}")   # Modify — partial update
@app.delete("/transactions/{id}")  # Remove
```

### Path parameters vs query parameters

```python
# Path parameter — part of the URL itself
@app.get("/transactions/{transaction_id}")
def get_transaction(transaction_id: str):
    return {"id": transaction_id}
# Call: GET /transactions/TXN20240101ABCD

# Query parameter — after the ?
@app.get("/transactions")
def list_transactions(status: str = None, page: int = 1):
    return {"status": status, "page": page}
# Call: GET /transactions?status=success&page=2
```

### Status codes

```python
from fastapi import status

@app.post("/customers", status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate):
    ...

@app.delete("/customers/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(id: str):
    ...
```

---

## 5. Pydantic — data validation

Pydantic lets you define a class with type hints. It automatically:
- Validates incoming data matches those types
- Converts compatible types (e.g. `"500"` → `500` for an `int` field)
- Raises clear errors if validation fails
- Generates the JSON schema that powers Swagger docs

### Basic model

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from decimal import Decimal

class TransactionCreate(BaseModel):
    customer_id: str
    amount: Decimal = Field(..., gt=0, description="Must be positive")
    currency: str = Field(default="INR", max_length=3)
    description: Optional[str] = None
```

Send this JSON to your endpoint:
```json
{
  "customer_id": "uuid-here",
  "amount": "499.00",
  "currency": "INR"
}
```

Pydantic parses `"499.00"` → `Decimal("499.00")` automatically.

### Field validators

```python
from pydantic import field_validator
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def must_have_uppercase(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        return v
```

### Separating input from output schemas

Never use the same model for requests and responses. Keep them separate:

```python
# What the client sends
class MerchantCreate(BaseModel):
    name: str
    email: EmailStr
    business_name: str

# What you return — excludes sensitive fields
class MerchantResponse(BaseModel):
    id: str
    name: str
    email: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}  # Lets Pydantic read SQLAlchemy ORM objects
```

### `from_attributes = True` — the bridge between ORM and Pydantic

```python
# Without it — this would fail:
db_merchant = db.query(Merchant).first()   # SQLAlchemy ORM object
MerchantResponse.model_validate(db_merchant)  # ❌ Pydantic can't read ORM objects

# With from_attributes = True inside model_config — this works:
MerchantResponse.model_validate(db_merchant)  # ✅ Pydantic reads ORM like a dict
```

> **Why this matters:** You never manually map `.id`, `.name`, `.email` from ORM to dict. Pydantic does it automatically via `from_attributes`.

---

## 6. Project structure

The structure that scales to MNC level:

```
paysync/
├── app/
│   ├── main.py              ← FastAPI app, middleware, route registration
│   │
│   ├── core/
│   │   ├── config.py        ← All environment variables (Pydantic Settings)
│   │   ├── database.py      ← SQLAlchemy engine + session factory
│   │   ├── security.py      ← JWT, bcrypt, API key generation
│   │   ├── dependencies.py  ← FastAPI Depends() — auth guards, DB sessions
│   │   └── exceptions.py    ← Custom exceptions + global handlers
│   │
│   ├── models/
│   │   └── models.py        ← SQLAlchemy ORM table definitions
│   │
│   ├── schemas/
│   │   └── schemas.py       ← Pydantic request/response models
│   │
│   ├── routers/
│   │   ├── auth.py          ← /auth/login, /auth/refresh
│   │   ├── merchants.py     ← /merchants CRUD
│   │   ├── customers.py     ← /customers CRUD
│   │   ├── transactions.py  ← /transactions — core payment logic
│   │   └── settlements.py   ← /settlements — daily payouts
│   │
│   ├── services/
│   │   ├── transaction_service.py  ← Business rules, idempotency, ledger
│   │   └── webhook_service.py      ← HMAC signing, delivery, retry
│   │
│   └── middleware/
│       └── middleware.py    ← Request ID, audit logging
│
├── alembic/                 ← Database migration scripts
├── tests/
│   └── test_paysync.py      ← Full test suite
├── .env                     ← Secrets (never commit this)
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

### The creation order — always follow this

```
1. database.py   → connect to Postgres
2. models.py     → define tables (SQLAlchemy)
3. schemas.py    → define API contracts (Pydantic)
4. services/     → write business logic
5. routers/      → wire up HTTP endpoints
6. main.py       → register everything
```

> **Why this order?** Each layer depends on the one before it. Routers import schemas. Schemas know nothing about the DB. Services import models. Models know nothing about HTTP. This separation means you can test each layer independently.

---

## 7. SQLAlchemy — ORM

SQLAlchemy lets you write Python classes instead of raw SQL. It maps Python objects to database tables.

### `declarative_base()` — the foundation

```python
from sqlalchemy.orm import declarative_base

Base = declarative_base()
```

`Base` is the parent class every table inherits from. It:
- Stores metadata about all your tables
- Acts as a central registry
- Enables `Base.metadata.create_all()` to generate SQL and create tables

```
declarative_base()
      ↓
  Base created
      ↓
  Models inherit Base  (class Merchant(Base), class Customer(Base) ...)
      ↓
  Base tracks all models
      ↓
  Base.metadata.create_all(bind=engine)
      ↓
  Tables created in PostgreSQL
```

### `Base.metadata` stores:

- All table names and columns
- Data types and constraints
- Indexes and foreign keys
- Relationships between tables

### Defining a table

```python
from sqlalchemy import Column, String, Boolean, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

class Merchant(Base):
    __tablename__ = "merchants"

    # Primary key — UUID, never auto-increment integers in a payments system
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name         = Column(String(255), nullable=False)
    email        = Column(String(255), unique=True, nullable=False, index=True)
    status       = Column(Enum(MerchantStatus), default=MerchantStatus.PENDING_KYC)
    is_deleted   = Column(Boolean, default=False)          # Soft delete — never hard delete financial data

    # Auto-managed timestamps
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    updated_at   = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship — SQLAlchemy loads related records automatically
    customers    = relationship("Customer", back_populates="merchant")
```

### The engine and session

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# One engine per app — your connection pool to Postgres
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # Keep 10 connections warm
    max_overflow=20,       # Allow 20 extra under high load
    pool_pre_ping=True,    # Check connection health before using
)

# Session factory — each request gets its own session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### `get_db()` — the dependency that manages sessions

```python
def get_db():
    db = SessionLocal()
    try:
        yield db          # ← FastAPI injects this session into your route
    except Exception:
        db.rollback()     # ← Rollback on any error
        raise
    finally:
        db.close()        # ← Always close, even if an exception occurs
```

```python
# Usage in a route
@app.get("/merchants/{id}")
def get_merchant(id: str, db: Session = Depends(get_db)):
    #                               ↑
    #               FastAPI calls get_db() automatically,
    #               passes the session here, closes it after
    return db.query(Merchant).filter(Merchant.id == id).first()
```

### Common DB operations

```python
# CREATE
merchant = Merchant(name="Swiggy", email="finance@swiggy.com")
db.add(merchant)
db.commit()
db.refresh(merchant)   # ← Pulls server-generated id and timestamps back into the object

# READ
merchant = db.query(Merchant).filter(Merchant.id == some_id).first()
merchants = db.query(Merchant).filter(Merchant.is_deleted == False).all()

# UPDATE
merchant.status = MerchantStatus.ACTIVE
db.commit()

# SOFT DELETE (never hard delete in finance)
merchant.is_deleted = True
merchant.deleted_at = datetime.utcnow()
db.commit()

# Row-level lock (prevents race conditions on wallet balance)
wallet = db.query(Wallet).filter(
    Wallet.customer_id == customer_id
).with_for_update().first()   # ← Locks this row until transaction commits
```

### Alembic — database migrations

Never use `Base.metadata.create_all()` in production. Use Alembic migrations instead — they track schema changes like Git tracks code.

```bash
# Initial setup
alembic init alembic

# Generate a migration from your model changes
alembic revision --autogenerate -m "add_merchant_daily_limit"

# Apply migrations to DB
alembic upgrade head

# Roll back one migration
alembic downgrade -1

# See migration history
alembic history
```

---

## 8. psycopg2 — the DB driver

SQLAlchemy is the ORM. psycopg2 is the low-level driver that actually speaks the PostgreSQL protocol.

```
FastAPI
  ↓
SQLAlchemy (ORM — translates Python to SQL)
  ↓
psycopg2  (driver — speaks PostgreSQL wire protocol)
  ↓
PostgreSQL
```

You rarely use psycopg2 directly. SQLAlchemy finds it automatically from your `DATABASE_URL`:

```
postgresql://user:password@localhost:5432/paysync
     ↑
     SQLAlchemy sees "postgresql://" → looks for psycopg2 → uses it
```

Install it as:

```bash
pip install psycopg2-binary   # Development (pre-compiled, no build tools needed)
pip install psycopg2          # Production (compiled from source, more reliable)
```

---

## 9. The full request lifecycle

Tracing a `POST /transactions` request through every layer:

```
1. Client sends:
   POST /api/v1/transactions
   X-API-Key: sk_live_abc123
   Body: { "customer_id": "...", "amount": "499.00", "payment_method": "upi" }

2. Uvicorn receives the HTTP request, passes it to FastAPI

3. Middleware runs first:
   - RequestIDMiddleware → attaches X-Request-ID header
   - AuditLogMiddleware → records the request for compliance

4. FastAPI matches the route → transactions.create_transaction()

5. Dependency injection fires:
   - Depends(get_db)                 → opens a DB session
   - Depends(get_merchant_from_api_key) → hashes the API key, looks up merchant

6. Pydantic validates the request body (TransactionCreate):
   - amount must be > 0
   - payment_method must be a valid enum
   - currency must be INR/USD/EUR/GBP/SGD
   → If anything fails: 422 response, no business logic runs

7. Router calls TransactionService.create_transaction(db, merchant, payload)

8. Service layer enforces business rules:
   - Is merchant KYC approved?        → if not: 422
   - Is customer active?              → if not: 422
   - Is wallet frozen?                → if not: 422
   - Does amount exceed merchant limit? → if so: 422
   - Idempotency check                → same key seen before? return cached result
   - with_for_update() lock on wallet → prevent race condition
   - Is balance sufficient?           → if not: 422

9. DB writes (atomic — all succeed or all roll back):
   - INSERT into transactions
   - UPDATE wallets SET balance = balance - 499.00
   - INSERT into ledger_entries

10. Background task queued (non-blocking):
    - WebhookService.dispatch_pending_webhooks → POSTs to merchant's webhook_url

11. Response serialized through TransactionResponse (Pydantic):
    - ORM object → Pydantic model → JSON
    - Sensitive fields excluded automatically

12. FastAPI returns 201 Created with the transaction JSON

13. get_db() finally block runs → DB session closed
```

---

## 10. Layer-by-layer story

### `database.py` — the engine room

`create_engine(DATABASE_URL)` is your one-time handshake with the DB. `SessionLocal` is a factory — every request gets its own session via `get_db()`, a generator that yields a session and closes it after the request, guaranteed. Nothing else in your app knows the DB URL.

### `models.py` — the table blueprint

`class Merchant(Base)` is Python telling SQLAlchemy what the DB table looks like. `Column(UUID, primary_key=True)` etc. The model lives in DB-land. In production, Alembic migrations create the physical tables — not `create_all()`.

### `schemas.py` — the JSON contract

Pydantic `BaseModel` is your gatekeeper for what goes **in** (request body) and **out** (response). `model_config = {"from_attributes": True}` is the bridge — it lets Pydantic read a SQLAlchemy ORM object like a dict, so `MerchantResponse.model_validate(db_merchant)` just works. No manual `.id`, `.name` mapping.

### `services/` — the business rules, isolated

Pure functions, no HTTP, no routes. `db.query(Transaction).filter(...).first()` for reads. `db.add()` → `db.commit()` → `db.refresh()` for writes. `db.refresh()` pulls the server-generated `id` back into your object. Keeping this separate means you can test business logic without spinning up a server.

### `routers/` — the orchestrators

`@router.post("/transactions", response_model=TransactionResponse, status_code=201)` does three things in one line: registers the route, tells FastAPI which schema to serialize the response through, and sets the HTTP status. `Depends(get_db)` is dependency injection — FastAPI calls `get_db()`, passes the session to your function, and closes it after. You never manage the session lifecycle manually.

### The payoff

FastAPI takes your return value (a SQLAlchemy ORM object), passes it through `TransactionResponse` (Pydantic schema), and the client gets clean validated JSON. The chain is:

```
PostgreSQL row → SQLAlchemy ORM object → Pydantic schema → JSON response
```

Each file has exactly one job.

---

## 11. OpenAPI — auto docs

FastAPI generates a complete OpenAPI schema from your code automatically — no separate documentation to maintain.

A **schema** is an abstract description of your API: what endpoints exist, what they accept, what they return. FastAPI derives this from:

- Route decorators (`@app.get`, `@app.post`)
- Pydantic models (request/response shapes)
- Type hints (path params, query params)
- `Field(...)` descriptions and constraints

```python
# All of this becomes part of the auto-generated docs:
@router.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=201,
    summary="Create a payment transaction",
    description="Processes a payment and debits the customer wallet. Pass an idempotency_key to safely retry.",
    tags=["Transactions"],
)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
):
    ...
```

Access at: `http://localhost:8000/docs`

---

## 12. Concurrency vs parallelism

These are frequently confused. FastAPI handles both differently.

**Concurrency** — doing multiple tasks at a time by switching between them while waiting.

```
Request 1: sent DB query → waiting for response...
  → while waiting, handle Request 2
  → DB response arrives → finish Request 1
```

**Parallelism** — doing multiple computations literally simultaneously (multiple CPU cores).

```
Core 1: processing Request 1
Core 2: processing Request 2   ← simultaneously, not taking turns
```

### Why concurrency wins for APIs

Most API time is spent **waiting** — waiting for DB queries, waiting for HTTP calls to payment providers, waiting for Redis. During that waiting time, your CPU is idle.

`async`/`await` lets FastAPI handle thousands of waiting requests concurrently on a single thread — no idle CPU.

```python
# Sync route — blocks the thread while waiting for DB
@app.get("/transactions/{id}")
def get_transaction(id: str, db: Session = Depends(get_db)):
    return db.query(Transaction).filter(Transaction.id == id).first()

# Async route — yields control while waiting, handles other requests
@app.get("/transactions/{id}")
async def get_transaction(id: str):
    transaction = await db.execute(select(Transaction).where(Transaction.id == id))
    return transaction.scalar()
```

> **PaySync uses sync routes with SQLAlchemy sync sessions** for simplicity. For extreme scale (10k+ RPS), switch to `asyncpg` + `SQLAlchemy async`.

---

## 13. PaySync creation flow

The order in which PaySync was built, and what you learn at each step:

```
Step 1 — database.py
         create_engine() · SessionLocal · get_db()
         Concept: connection pooling, session lifecycle

Step 2 — models.py
         Merchant, Customer, Wallet, Transaction, LedgerEntry ...
         Concept: ORM mapping, relationships, indexes, soft deletes

Step 3 — schemas.py
         MerchantCreate, TransactionCreate, TransactionResponse ...
         Concept: input/output separation, validators, from_attributes

Step 4 — alembic
         alembic revision --autogenerate
         Concept: schema migrations, version control for DB

Step 5 — core/security.py
         bcrypt, JWT, API key generation with SHA-256 hashing
         Concept: never store raw secrets, hash everything

Step 6 — core/dependencies.py
         get_current_user(), get_merchant_from_api_key(), require_super_admin()
         Concept: Depends() chains, reusable auth guards

Step 7 — core/exceptions.py
         PaySyncException, NotFoundError, BusinessRuleError ...
         Concept: custom exception hierarchy, global handlers

Step 8 — services/transaction_service.py
         KYC gate, idempotency, with_for_update(), ledger writes
         Concept: business logic isolation, race condition prevention

Step 9 — routers/ (auth, merchants, customers, transactions, settlements)
         Full CRUD, pagination, filtering, background tasks
         Concept: APIRouter, route grouping, BackgroundTasks

Step 10 — middleware/
          RequestIDMiddleware, AuditLogMiddleware
          Concept: cross-cutting concerns, compliance logging

Step 11 — main.py
          Register routers, middleware, exception handlers, CORS
          Concept: app composition, middleware ordering

Step 12 — tests/
          TestClient, SQLite fixture, 30+ tests
          Concept: dependency override, isolated test DB
```

---

## Quick reference

### Install

```bash
pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary \
            pydantic pydantic-settings python-jose passlib \
            python-multipart python-dotenv httpx pytest
```

### Environment variables (`.env`)

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/paysync
SECRET_KEY=minimum-32-character-random-string
APP_ENV=development
DEBUG=true
```

### Common patterns

```python
# Dependency injection
db: Session = Depends(get_db)
merchant: Merchant = Depends(get_merchant_from_api_key)
user: User = Depends(require_super_admin)

# Pagination
page: int = Query(default=1, ge=1)
page_size: int = Query(default=20, ge=1, le=100)
offset = (page - 1) * page_size
results = db.query(Model).offset(offset).limit(page_size).all()

# Soft delete
model.is_deleted = True
model.deleted_at = datetime.utcnow()
db.commit()

# Background task
background_tasks.add_task(some_function, arg1, arg2)

# Row lock (prevent race conditions)
record = db.query(Model).filter(...).with_for_update().first()
```

---

*Built while learning FastAPI by constructing PaySync — a production-grade multi-tenant payment gateway.*
