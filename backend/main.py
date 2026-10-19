#modules internes
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from routes.realtime import hub
from routes.game_mode.duel_mode import sweeper
from all import db_guard
from fastapi.middleware.cors import CORSMiddleware

##"routes"
from routes.user import router as user_router
from routes.game import router as game_router
from routes.shop import router as shop_router


from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


@asynccontextmanager
async def lifespan(_app):
    hub.bind(asyncio.get_running_loop())     # permet aux routes synchrones de pousser des messages aux sockets
    task = asyncio.create_task(sweeper())    # delais d'inactivite / deconnexion
    yield
    task.cancel()
    hub.bind(None)


app = FastAPI(dependencies=[Depends(db_guard)], lifespan=lifespan)
app.add_middleware(CORSMiddleware , 
                   allow_origins = ["*"],
                   allow_credentials = True,
                   allow_methods = ["*"],
                   allow_headers = ["*"]
                   
                   )  


app.include_router(user_router)
app.include_router(game_router)
app.include_router(shop_router)



@app.get('/health')
def getHealth():
    return "En Bonne Sante"

@app.get('/whatsup')
def getStatus():
    return "caleuuuuu"


# handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": jsonable_encoder(exc.errors(), custom_encoder={Exception: str})}
    )
