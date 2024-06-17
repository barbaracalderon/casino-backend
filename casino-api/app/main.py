from fastapi import FastAPI, HTTPException
from app.routes.player_route import router as player_router 
from app.routes.balance_route import router as balance_router
from app.routes.transaction_route import router as transaction_router
from app.exceptions.player_not_found_exception import PlayerNotFoundException


app = FastAPI()


app.include_router(player_router, prefix="/players", tags=["players"])
app.include_router(balance_router, prefix="/balance", tags=["balance"])
app.include_router(transaction_router, prefix="/transactions", tags=["transactions"])
