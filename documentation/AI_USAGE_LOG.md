# AI Usage Log
Captures the prompts and tools used so that reviewers can visualize how AI was leveraged in development.

## Tools Used
- **FastAPI** - High-performance Python web framework for building APIs
- **SQLAlchemy** - Secure database interactions
- **JWT** - Authentication tokens and authorization
- **Python** - Primary programming language for backend development
- **ChatGPT** - AI-powered assistant for code and automation

## Example Prompts

**Code Development**
1. Generate SQLAlchemy models for a banking service: Users, Accounts, Transactions, Cards. Include foreign keys, timestamps, and basic constraints.

2. Generate JWT logic, password hashing, and signup/login endpoints in one block.

3. Write pytest unit tests for my withdraw, deposit, and transfer functions in accounts.py. Make sure to test:
    - Depositing a positive amount updates the balance.
    - Depositing a negative amount raises an error.
    - Withdrawing more than the balance raises HTTPException.
    - Transferring funds between accounts updates both balances correctly.
    - Return test functions only, with setup code using SQLAlchemy in-memory SQLite.
    
4. Generate pytest integration tests for my FastAPI accounts routes using TestClient. Test the following API endpoints:
    - POST /accounts/ creates a new account.
    - GET /accounts/ lists accounts for the authenticated user.
    - POST /accounts/{id}/deposit successfully updates balance.
    - POST /accounts/{id}/withdraw blocks if insufficient balance.
    - POST /accounts/{from_id}/transfer/{to_id} moves money correctly.

**System Design and Architecutre**
1. . Extend my accounts.py routes to handle deposits, withdrawals, and transfers. Add error handling for edge cases like insufficient funds, invalid accounts, and negative amounts.

**Documentation**
1. What are the necessary components to include when discussing security considerations for a REST service?


## Challenges and Solutions

## Manual Intervention
1. Establishment of a .env file to securely store sensitive configuration and environment variables.

2. Generation and storage of a JWT secret key within the .env file for secure authentication handling.

3. Implementation of a .gitignore file to prevent accidental exposure of confidential information in version control.