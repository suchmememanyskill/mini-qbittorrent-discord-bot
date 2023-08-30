import os, qbittorrentapi

class Env:
    def __init__(self, bot_token : str, qbit_port : int | str | None = None, qbit_host : str | None = None, qbit_user : str | None = None, qbit_pass : str | None = None, locations : dict = None):
        if bot_token is None:
            raise Exception("Missing BOT_TOKEN env var")
        
        if locations is None or len(locations) <= 0:
            raise Exception("No locations specified")

        self.token = bot_token
        self.locations = locations
        
        self.qbit_host = qbit_host or "localhost"
        self.qbit_port = int(qbit_port or 8080)
        self.qbit_user = qbit_user or "admin"
        self.qbit_pass = qbit_pass or "adminadmin"
        self.client_params = {
            "host": self.qbit_host,
            "port": self.qbit_port,
            "username": self.qbit_user,
            "password": self.qbit_pass,
        }

ENV : Env = None

def probe_environment():
    global ENV

    locations = {}
    for x in os.environ:
        if x.startswith("FOLDER_"):
            locations[x[7:].capitalize()] = os.environ[x]
    
    ENV = Env(
        os.getenv("BOT_TOKEN", os.getenv("TOKEN")),
        os.getenv("QBIT_PORT"),
        os.getenv("QBIT_HOST"),
        os.getenv("QBIT_USER"),
        os.getenv("QBIT_PASS"),
        locations
    )

probe_environment()