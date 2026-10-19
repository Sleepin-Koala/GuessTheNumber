#modules internes
import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from routes.realtime import hub
from routes.auth import authenticate
from security import SecurityMiddleware, ALLOWED_ORIGINS, client_ip
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


# ordre: db_guard (verrou) puis authenticate (jeton): toute route est protegee par defaut
_DOCS = os.environ.get("GTN_DOCS") == "1"      # la documentation interactive decrit toute l'API: desactivee par defaut
app = FastAPI(dependencies=[Depends(db_guard), Depends(authenticate)], lifespan=lifespan,
              docs_url="/docs" if _DOCS else None, redoc_url=None, openapi_url="/openapi.json" if _DOCS else None)
app.add_middleware(SecurityMiddleware)                      # taille, debit, en-tetes (interieur)
app.add_middleware(CORSMiddleware,                          # exterieur: ajoute les en-tetes CORS meme aux erreurs 401/429
                   allow_origins = ALLOWED_ORIGINS,
                   allow_credentials = False,               # le jeton voyage dans Authorization, pas dans un cookie
                   allow_methods = ["GET", "POST"],
                   allow_headers = ["Authorization", "Content-Type"],
                   expose_headers = ["Retry-After"])      # le navigateur doit pouvoir lire le delai d'attente d'un 429


app.include_router(user_router)
app.include_router(game_router)
app.include_router(shop_router)



@app.get('/health')
def getHealth():
    return "En Bonne Sante"

@app.get('/whoami')
def whoami(request: Request):
    """Adresse que le serveur croit etre celle de l'appelant. Sert a verifier le reglage GTN_PROXY_HOPS apres un deploiement
    derriere un proxy: l'adresse affichee doit etre la tienne (ex. celle donnee par https://ifconfig.me)."""
    return {"ip": client_ip(request.scope)}


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
