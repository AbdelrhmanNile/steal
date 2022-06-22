import re
import json
import requests


class StealApi:
    def __init__(self):
        self.url = (
            "https://data.mongodb-api.com/app/data-hfsyl/endpoint/data/v1/action/find"
        )
        self.headers = {
            "Content-Type": "application/json",
            "Access-Control-Request-Headers": "*",
            "api-key": "eLqlbfBx4Vj5qYtweN4e2aadnaE14962uJqT2cfXUyOnfvZkxJgF1QTrgg83L1A7",
        }

    def search(self, game_name):
        # keyword = str(re.compile(f".*{game_name}.*", re.I))

        try:
            payload = json.dumps(
                {
                    "collection": "games",
                    "database": "gamesdb",
                    "dataSource": "Cluster0",
                    "filter": {"name": {"$regex": f"{game_name}", "$options": "$i"}},
                }
            )
            # "filter": {"name": {"$regex": f"{game_name}", "$options": "$i"}},

            response = requests.request(
                "POST", self.url, headers=self.headers, data=payload
            )
            data = json.loads(response.text)

            return data["documents"]
        except requests.exceptions.ConnectionError:
            return None
