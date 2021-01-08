import mariadb

class StatsRepo:
    def __init__(self, user, password, host, port, database):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.conn = None
        self.cur = None

        
    
    def connect(self):
        self.conn = mariadb.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
            autocommit=True
        )
        self.cur = self.conn.cursor()


    def check_connection(self) -> bool:
        if self.cur is None or self.conn is None:
            self.connect()
            return False
        return True


    def get_data(self):
        self.check_connection()
        
        self.cur.execute(
            "SELECT * FROM minecraft.k4PlayerTracker"
        )

        
        ret = {}
        
        for (player_id, time, action) in self.cur:
            if player_id not in ret:
                ret[player_id] = []
            
            ret[player_id].append([time, action])
        
        to_return = []

        for player in ret:
            _logs = sorted(ret[player], key=lambda x: x[0], reverse=True)
            
            player_dict = {
                "player_id": player,
                "logs": []
            }

            if len(_logs) < 2:
                size_to_get = 1
            else:
                size_to_get = 2
            for i in range(0,size_to_get):

                log_dict = {
                    "action": _logs[i][1],
                    "time": _logs[i][0]
                }
                player_dict["logs"].append(log_dict)
            to_return.append(player_dict)

        return to_return
