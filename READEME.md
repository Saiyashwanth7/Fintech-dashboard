# Finance Data Processing and Access Control Backend

A role-based finance dashboard backend built with FastAPI, SQLAlchemy, and SQLite. Supports financial record management, user access control, and aggregated dashboard analytics.

---

## Tech Stack

- **Framework:** FastAPI
- **Database:** SQLite via SQLAlchemy ORM
- **Auth:** JWT (python-jose) + bcrypt password hashing
- **Testing:** pytest + FastAPI TestClient
- **Validation:** Pydantic v2

---

## Setup

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd <project-folder>

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file in project root
DB_URL=sqlite:///./finance.db
SECRET_KEY=your-secret-key-here-make-it-long
ALGORITHM=HS256

# 5. Run the server
uvicorn main:app --reload
```

API docs available at: `http://localhost:8000/docs`

---

## Roles & Permissions

| Action | Viewer | Analyst | Admin |
|---|---|---|---|
| View own profile | ✅ | ✅ | ✅ |
| Read financial records | ✅ | ✅ | ✅ |
| Filter / paginate records | ✅ | ✅ | ✅ |
| View dashboard summaries | ❌ | ✅ | ✅ |
| Create financial records | ❌ | ❌ | ✅ |
| Update financial records | ❌ | ❌ | ✅ |
| Delete financial records | ❌ | ❌ | ✅ |
| Manage users | ❌ | ❌ | ✅ |
| Toggle user active status | ❌ | ❌ | ✅ |

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/` | Register new user |
| POST | `/auth/token` | Login — returns JWT token |

### Financial Records
| Method | Endpoint | Description |
|---|---|---|
| GET | `/records/` | List records (filter + paginate) |
| POST | `/records/` | Create record (Admin only) |
| GET | `/records/{id}` | Get single record |
| PUT | `/records/{id}` | Update record (Admin only) |
| DELETE | `/records/{id}` | Soft delete record (Admin only) |

**Filter parameters on GET `/records/`:**
- `type` — `income` or `expense`
- `category` — string match
- `from_date` — `YYYY-MM-DD`
- `to_date` — `YYYY-MM-DD`
- `skip` — pagination offset (default 0)
- `limit` — page size (default 10, max 100)

### Dashboard (Analyst + Admin only)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/dashboard/` | Total income, expenses, net balance |
| GET | `/dashboard/by-category` | Breakdown per category |
| GET | `/dashboard/trends` | Monthly income/expense totals |
| GET | `/dashboard/recents` | Last 10 transactions |

### Users (Admin only)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/users/me` | Own profile (any role) |
| GET | `/users/` | List all users |
| GET | `/users/{id}` | Get user by ID |
| PUT | `/users/{id}` | Update user name/email |
| PATCH | `/users/{id}` | Toggle active/inactive status |

---

## Running Tests

```bash
pytest test/ -v
```

Tests are organised by role — `test_admin.py`, `test_analyst.py`, `test_viewer.py` — each validating that role's permissions explicitly.

The test suite uses a separate in-memory SQLite database with dependency injection override so production data is never touched.

---

## Assumptions & Design Decisions

**Role design:** Analyst is read-only for financial records. Only Admin can create, update, or delete records. In a finance system, write access to records should be restricted and auditable — giving Analysts write access would undermine data integrity.

**Soft delete:** Records are flagged `is_deleted=True` rather than removed from the database. This preserves the audit trail for financial data, which may be required for compliance or historical reporting.

**Category normalisation:** All category names are stored as lowercase and stripped of whitespace on creation. This prevents `"Food"` and `"food"` appearing as separate categories in dashboard aggregations.

**Dashboard aggregations:** The trends endpoint uses SQLite's `strftime('%Y-%m', date)` for monthly grouping. Note: `%Y` is 4-digit year, `%m` is 2-digit month — SQLite format differs from Python's strftime in some edge cases.

**User status:** Inactive users cannot authenticate. The `is_active` flag is checked during login. Admins can toggle status via `PATCH /users/{id}`.

**Token expiry:** JWT tokens expire after 1 hour. This is a reasonable balance between usability and security for a dashboard application.

**SQLite choice:** SQLite was chosen for simplicity and zero-configuration setup. For production, PostgreSQL would be preferred for concurrent write support and ACID compliance at scale.

---

## Project Structure

```
├── main.py               # FastAPI app, router registration
├── models.py             # SQLAlchemy models (Users, FinancialRecords)
├── database.py           # DB engine, session, get_db dependency
├── config.py             # Environment variable loading
├── routers/
│   ├── auth.py           # Registration, login, JWT utilities
│   ├── finance.py        # Financial records CRUD + filtering
│   ├── dashboard.py      # Aggregated analytics endpoints
│   ├── users.py          # User management
│   └── pydantic_models.py # Request/response schemas
└── test/
    ├── conftest.py        # Shared fixtures, test DB setup
    ├── test_admin.py      # Admin role tests
    ├── test_analyst.py    # Analyst role tests
    ├── test_viewer.py     # Viewer role tests
    └── test_health.py     # Health check test
```