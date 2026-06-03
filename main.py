from fastapi import FastAPI
from routerOAuth2 import root_r

app = FastAPI()
app.include_router(root_r.router)

