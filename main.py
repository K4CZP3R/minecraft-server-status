import minestat, socket, mcrcon
from os import getenv
from fastapi import FastAPI

app = FastAPI()

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
    
@app.get("/")
def show_server():
    server_addr = getenv("SERVER_HOSTNAME")
    server_port = int(getenv("SERVER_PORT"))
    rcon_pass = getenv("RCON_PASSWORD")
    rcon_port = int(getenv("RCON_PORT"))
    ms = minestat.MineStat(server_addr, server_port)
    
    
    if rcon_pass is not None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server_addr, rcon_port))
        result = mcrcon.login(sock, rcon_pass)
        if result:
            players = mcrcon.command(sock,"list")

            players = extract_player_list(players)
            ms.set_players(players)
    

    return ms