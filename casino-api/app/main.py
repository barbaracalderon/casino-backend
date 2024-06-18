from fastapi import FastAPI, HTTPException
from app.routes.player_route import router as player_router 
from app.routes.balance_route import router as balance_router
from app.routes.transaction_route import router as transaction_router
from app.exceptions.player_not_found_exception import PlayerNotFoundException


app = FastAPI(
    title="Casino API",
    description="This is a REST API to manage players, balances and transactions of a Casino.",
    version="1.0.0",
    contact={
        "name": "Barbara Calderon",
        "url": "http://www.github.com/barbaracalderon",
        "email": "bcalderoni.ti@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)


app.include_router(player_router, prefix="/players", tags=["players"])
app.include_router(balance_router, prefix="/balance", tags=["balance"])
app.include_router(transaction_router, prefix="/transactions", tags=["transactions"])
