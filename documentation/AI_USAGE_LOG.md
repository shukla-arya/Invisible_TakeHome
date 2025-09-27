# AI Usage Log
Captures the prompts and tools used so that reviewers can visualize how AI was leveraged in development.

## Tools Used
- **FastAPI** - Web framework
- **SQLAlchemy** - Database interactions
- **JWT** - Authentication tokens
- **Python** - Language of code
- **ChatGPT** - Recepient of prompting

## Example Prompts
1. Generate SQLAlchemy models for a banking service: Users, Accounts, Transactions, Cards. Include foreign keys, timestamps, and basic constraints.
2. Generate JWT logic, password hashing, and signup/login endpoints in one block.
3. Extend my accounts.py routes to handle deposits, withdrawals, and transfers. Add error handling for edge cases like insufficient funds, invalid accounts, and negative amounts.
4. Write pytest unit tests for my withdraw, deposit, and transfer functions in accounts.py. Make sure to test:
    - Depositing a positive amount updates the balance.
    - Depositing a negative amount raises an error.
    - Withdrawing more than the balance raises HTTPException.
    - Transferring funds between accounts updates both balances correctly.
    - Return test functions only, with setup code using SQLAlchemy in-memory SQLite.
5. Generate pytest integration tests for my FastAPI accounts routes using TestClient. Test the following API endpoints:
    - POST /accounts/ creates a new account.
    - GET /accounts/ lists accounts for the authenticated user.
    - POST /accounts/{id}/deposit successfully updates balance.
    - POST /accounts/{id}/withdraw blocks if insufficient balance.
    - POST /accounts/{from_id}/transfer/{to_id} moves money correctly.
6. What are the necessary components to include when discussing security considerations for a REST service?

## Challenges and Solutions

## Manual Intervention
1. Creation of the .env file for holding secret information.
2. Creation of the JWT secret key to be stored in .env file.
3. Creation of .gitignore file so that no secret info is passed to GitHub.
4. Tying together all the routes to be accessible by the API in main.py.