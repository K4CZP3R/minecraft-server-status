import minestat, socket, mcrcon

from sanic import Sanic
from sanic.response import json
from sanic_cors import CORS, cross_origin

app = Sanic()
CORS(app)

def extract_player_list(input_list):
    input_list = input_list.replace("\n","")
    formatted_list = ""
    ignore_next = False
    for i in range(0, len(input_list)):
        if input_list[i] == "§":
            ignore_next = True
            continue

        if ignore_next:
            ignore_next = False
            continue

        formatted_list += input_list[i]

    splitted_list = formatted_list.split("default:")
    if len(splitted_list) != 2:
        return []
    formatted_list = formatted_list.replace(" ","").split("default:")[1]
    

    return formatted_list.split(",")
    


@app.route("/<server_addr:string>")
async def test(request, server_addr):
    a = minestat.MineStat(server_addr, 25565).__dict__
    
    rcon_pass = request.args.get("rcon_pass", None)
    
    if rcon_pass is not None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server_addr, 25575))
        result = mcrcon.login(sock, rcon_pass)
        if result:
            players = mcrcon.command(sock,"list")

            players = extract_player_list(players)
            a["players"] = players
        else:
            a["players"] = []
    

    return json(a)

app.run(host="0.0.0.0", port=8000)