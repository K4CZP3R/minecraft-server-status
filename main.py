import minestat
from os import getenv
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from stats_repo import StatsRepo
from mariadb import OperationalError, InterfaceError, ProgrammingError
from ws_connection_manager import WsConnectionManager
import asyncio, time

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)
stats_repo = StatsRepo(
    getenv('DB_USER'),
    getenv('DB_PASS'),
    getenv('DB_HOST'),
    int(getenv('DB_PORT')),
    getenv('DB_NAME')
)

ws_manager = WsConnectionManager()

try:
    stats_repo.connect()
except Exception:
    print("Can't connect to the database!")


@app.get("/")
async def show_server():
    server_addr = getenv("SERVER_HOSTNAME")
    server_port = int(getenv("SERVER_PORT"))
    ms = minestat.MineStat(server_addr, server_port)
    return ms


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.send_personal_message(stats_repo.get_data(), websocket)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


@app.exception_handler(OperationalError)
async def maria_oe_handler(request: Request, exc: OperationalError):
    return JSONResponse(
        status_code=419,
        content={"success": False, "content": exc.__dict__}
    )


@app.exception_handler(InterfaceError)
async def maria_ie_handler(request: Request, exc: InterfaceError):
    stats_repo.conn = None
    return JSONResponse(
        status_code=418,
        content={"success": False, "content": exc.__dict__}
    )


async def ws_background():
    old_data = {}
    last_check = 0
    check_every = 60
    while True:
        try:
            await asyncio.sleep(1)
            new_data = stats_repo.get_data()

            if new_data == old_data and int(time.time()) - last_check < check_every:
                continue
            print("Broadcasting new information!")
            old_data = new_data
            last_check = int(time.time())
            await ws_manager.broadcast(new_data)
        except ProgrammingError:
            print("Can't connect to the database.")
            await asyncio.sleep(60)


@app.on_event('startup')
async def startup_event():
    task1 = asyncio.create_task(
        ws_background()
    )
    task1
