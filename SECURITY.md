# Security Considerations
Demonstrates the risks associated with the application and the best practices to prevent data leakage and misinformation.

## Authentication and Authorization
- Users authenticate via email and password.
    - The passwords are never stored in plain text.
    - Authenticated users can create their own accounts, depisot, withdraw, and transfer money with accounts they own.
    - Ownership checks are in place to prevent users from manipulating other users' accounts.
- Once successful, the app issues a JWT signed with a secret key (stored in .env).
- Access tokens have a short lifetime (30 minutes) to limit risk if stolen.


## Data Protection
- All sensitive keys and database credentials are stored in a `.env` file. 
- JWT is used for secure user authentication and session management.
- `.gitignore` is used for sensitive files to be excluded from version control.