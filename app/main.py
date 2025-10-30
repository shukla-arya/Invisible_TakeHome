'''
Acts as the FastAPI entry point to include the routers.
Ties all the routes files together so now they are accessible via API.
'''

# Imports
from fastapi import FastAPI
from app.routes.auth import router as auth_router
from app.routes.accounts import router as accounts_router
from app.routes.transactions import router as transactions_router
from app.routes.cards import router as cards_router

app = FastAPI(title="Banking API", version="1.0.0")

# Include all routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(accounts_router, prefix="/accounts", tags=["Accounts"])
app.include_router(transactions_router, prefix="/transactions", tags=["Transactions"])
app.include_router(cards_router, prefix="/cards", tags=["Cards"])

# Optional root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to the Banking API"}
