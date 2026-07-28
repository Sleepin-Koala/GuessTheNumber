#modules internes
from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware

##"routes"
from routes.user import router as user_router
from routes.game import router as game_router
from routes.multiplayer import router as multi_router
from routes.shop import router as shop_router


from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


app = FastAPI()
app.add_middleware(CORSMiddleware , 
                   allow_origins = ["*"],
                   allow_credentials = True,
                   allow_methods = ["*"],
                   allow_headers = ["*"]
                   
                   )  


app.include_router(user_router)
app.include_router(game_router)
app.include_router(multi_router)
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
    body = await request.body()
    print(f"Invalid body: {body.decode('utf-8', errors='ignore')}")
    # Return the default 422 response
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": body.decode('utf-8', errors='ignore')}
    )
