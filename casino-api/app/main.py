from fastapi import FastAPI, HTTPException
from app.routes.player_route import router as player_router 
from app.routes.balance_route import router as balance_router
from app.routes.transaction_route import router as transaction_router
from app.exceptions.player_not_found_exception import PlayerNotFoundException
from app.handlers.http_handler import http_exception_handler
from app.handlers.player_handler import player_not_found_exception_handler

app = FastAPI()

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(PlayerNotFoundException, player_not_found_exception_handler)

app.include_router(player_router, prefix="/players", tags=["players"])
app.include_router(balance_router, prefix="/balance", tags=["balance"])
app.include_router(transaction_router, prefix="/transactions", tags=["transactions"])
