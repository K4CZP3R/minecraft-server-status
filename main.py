import minestat, socket, mcrcon
from os import getenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

    
@app.get("/")
def show_server():
    server_addr = getenv("SERVER_HOSTNAME")
    server_port = int(getenv("SERVER_PORT"))
    ms = minestat.MineStat(server_addr, server_port)
    return ms