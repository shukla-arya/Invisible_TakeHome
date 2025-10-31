# Invisible_TakeHome
A take home assignment to demonstrate technical skills for the Software Engineer (Forward Deployed) role at Invisible. This project is a modular banking API that leverages AI tools.

## Features
- Develops a REST service that would be used by a bank.
- Utilizes AI-driven development practices for design and implementation.
- Contains a usage log for when AI intervention was supplemented.

## Technology Stack
- **FastAPI** - High-performance Python web framework for building APIs
- **SQLAlchemy** - Secure database interactions
- **JWT** - Authentication tokens and authorization
- **Python** - Primary programming language for backend development
- **ChatGPT** - AI-powered assistant for code and automation

## Environment Setup

1. **Clone the Repository**
```bash
   git clone https://github.com/yourusername/<repo>.git
   cd <repo>
```

2. **Activating the Environment**
```bash
   python -m venv venv
   venv\Scripts\activate # for Windows
   source venv/bin/activate # Linux/macOS
```

## Installing Dependencies

**Option 1: Install from File**
```bash
pip install -r requirements.txt
```

**Option 2: Manual Installation**
```bash
pip install fastapi uvicorn sqlalchemy pydantic pydantic[email] pytest httpx passlib python-jose python-dotenv passlib[bcrypt] cryptography jwt werkzeug
```

## API Documentation

### Authentication
- `POST /auth/register` – Register a new user.  
- `POST /auth/login` – Authenticate and receive an access token.  

### Accounts
- `POST /accounts` – Create a new account for the authenticated user.  
- `GET /accounts` – Retrieve all accounts belonging to the authenticated user.  

### Cards
- `POST /cards/` - Creates a new card linked to an existing account.
- `GET /cards/` - Lists all cards belonging to the authenticated user.

### Transactions
- `POST /transactions/deposit` – Deposit funds into an account.  
- `POST /transactions/withdraw` – Withdraw funds from an account.  
- `POST /transactions/transfer` – Transfer funds between accounts.

## Database Connection

The entities are uploaded to a SQLite database. These commands will populate the database with records of users, account, transaction, and card information.
```bash
# To populate the database
python -m app.database.seed_database

# To confirm the records were inserted
python -m app.database.verify_database
```

## Unit Tests

Navigate to the project root. This command will run the functions in the `tests   folder and validate the behavior of the database.
```bash
python -m pytest -v tests
```

## Run the API
Start the server.
```bash
# From the project root
univorn app main:app --reload
```

Navigate to the docs.
```bash
http://127.0.0.1:8000/docs
```
**Note:** Testing for signup, login, accounts, transactions, and cards can be performed directly in the browser. The UI will prompt request for bodies, query parameters, and headers.