import minestat

from sanic import Sanic
from sanic.response import json


app = Sanic()

@app.route("/<server_addr:string>")
async def test(request, server_addr):
    return json(minestat.MineStat(server_addr,25565).__dict__)

app.run(host="0.0.0.0", port=8000)