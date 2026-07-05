#modules internes
from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware

#from all_ import *



##"routes"
from routes.user import router as user_router
from routes.game import router as game_router
from routes.multiplayer import router as multi_router
from routes.shop import router as shop_router



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

