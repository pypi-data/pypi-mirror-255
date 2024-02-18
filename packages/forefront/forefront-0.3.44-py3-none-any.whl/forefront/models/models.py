import requests

class Models:
    def __init__(self, client):
        self.client = client
        self.default_model = client.default_model
        self.uri='/v1/models'
        

    def list_foundation_models(self):
        """
        List foundation models.

        :return: The API's response as Model objects.
        """
        response = requests.get(
            self.client.api_url + self.uri + '/list?tag=foundation',
            headers=self.client.headers
        )
        if response.status_code == 200:
            
            models = [Model(m) for m in response.json()]
            return models
        
    def list_community_models(self):
        """
        List community models.

        :return: The API's response as Model objects.
        """
        response = requests.get(
            self.client.api_url + self.uri + '/list?tag=community',
            headers=self.client.headers
        )
        if response.status_code == 200:
            
            models = [Model(m) for m in response.json()]
            return models
        else:
            print(response.json())
    
class Model:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.team_id = data['teamId']
        self.model_string = data['modelString']
        self.model_type = data['modelType']
        self.public = data['public']
        self.license = data['license']
        self.created_at = data['createdAt']
        self.readme_url = data['readmeUrl']
