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
```

## Installing Dependencies

**Option 1: Install from File**
```bash
pip install -r requirements.txt
```

**Option 2: Manual Installation**
```bash
pip install fastapi uvicorn sqlalchemy pydantic pytest httpx passlib python-jose python-dotenv passlib[bcrypt] cryptography
```

## API Documentation

### Authentication
- `POST /auth/register` – Register a new user.  
- `POST /auth/login` – Authenticate and receive an access token.  

### Accounts
- `POST /accounts` – Create a new account for the authenticated user.  
- `GET /accounts` – Retrieve all accounts belonging to the authenticated user.  

### Transactions
- `POST /transactions/deposit` – Deposit funds into an account.  
- `POST /transactions/withdraw` – Withdraw funds from an account.  
- `POST /transactions/transfer` – Transfer funds between accounts.
