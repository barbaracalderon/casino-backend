from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions.player_not_found_exception import PlayerNotFoundException


async def player_not_found_exception_handler(request: Request, exc: PlayerNotFoundException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail}
    )
