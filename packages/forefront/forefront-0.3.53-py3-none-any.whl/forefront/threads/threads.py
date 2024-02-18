
import requests

class Threads:
    def __init__(self, client):
        self.client = client
        self.default_model = client.default_model
        self.uri = "/v1/threads"

    def create(self, name: str,id:str = None,  user_id: str = None, group_id: str = None, metadata: dict = None):
        obj = {
            "name": name,
        }
        if id:
            obj["id"] = id
        if user_id:
            obj["user_id"] = user_id
        if group_id:
            obj["group_id"] = group_id
        if metadata:
            obj["metadata"] = metadata

        response = requests.post(
            self.client.api_url + self.uri + "/create",
            json=obj,
            headers=self.client.headers
        )
        
        if response.status_code == 200:
            print(response.json())
            return Thread(self.client, response.json())
        
        else:
            print(response.text())
        
    def get_by_id(self, id: str):
        response = requests.get(
            self.client.api_url + self.uri + "/" + id,
             headers=self.client.headers
        )
        if response.status_code == 200:
            return Thread(self.client, response.json(), response.json()["messages"])
        
    def list(self):
        response = requests.get(
            self.client.api_url + self.uri + "/list",
             headers=self.client.headers
        )
        if response.status_code == 200:
            return [Thread(self.client, x) for x in response.json()]
        else:
            print(response.text)


class Thread:
    def __init__(self, client, data, messages = None):
        self.client = client
        self.uri = "/v1/threads"
        self.id = data["id"]
        self.name = data["name"]
        self.user_id = data["userId"] if "userId" in data else None
        self.group_id = data["groupId"] if "groupId" in data else None
        self.metadata = data["metadata"] if "metadata" in data else None
        if messages:
            self.messages = [Message(x) for x in messages]
    
        
    def add(self, role: str, content: str,):
        obj = {
            "content": content,
            "role": role,
        }
        response = requests.post(
            self.client.api_url + self.uri + "/" + self.id,
            json=obj,
            headers=self.client.headers
        )
        if response.status_code == 200:
            return 'ok'
        else:
            print(response.text)

    def get_messages(self):
        response = requests.get(
            self.client.api_url + self.uri + "/" + self.id ,
             headers=self.client.headers
        )
        if response.status_code == 200:
            print(response.json())
            return [Message(x) for x in response.json()["messages"]]
        else:
            print(response.text)



class Message:
    def __init__(self, data):
        self.role = data["role"]
        self.content = data["content"]
        self.type = data["type"]
        self.created_at = data["createdAt"]
        self.model = data["modelId"]

    def to_json(self):
        return {
            "role": self.role,
            "content": self.content,
            "type": self.type,
            "createdAt": self.created_at,
            "modelId": self.model
        }
