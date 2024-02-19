from meowerclient import MeowerClient
import json as j

with open("token.json", "r+") as f:
    f.seek(0)
    data = j.load(f)
    f.close()

client = MeowerClient()
client.RUNCLIENT("SpeedBee411", data["token"])