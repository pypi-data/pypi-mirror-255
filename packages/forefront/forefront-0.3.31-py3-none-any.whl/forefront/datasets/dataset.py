import requests
import json
from ..utils import is_kebab_case

class Datasets:
    def __init__(self, client):
        self.client = client
        self.default_model = client.default_model
        self.uri='/v1/datasets'
        

    def list(self):
        """
        List all datasets.

        :return: The API's response as Dataset objects.
        """
        response = requests.get(
            self.client.api_url + self.uri + '/list',
            headers=self.client.headers
        )
        if response.status_code == 200:
            datasets = [Dataset(self.client, d) for d in response.json()]
            return datasets
        
    def get_by_id(self, id):
        """
        Get a dataset by id.

        :param id: The id of the dataset
        :return: The API's response as a Dataset object.
        """
        print('This is deprecated, use get_by_name instead')
        response = requests.get(
            self.client.api_url + self.uri + '/' + id,
            headers=self.client.headers,
        )
        if response.status_code == 200:
            return Dataset(self.client, response.json())
        
    def get_by_name(self, name):
        """
        Get a dataset by name.

        :param id: The name of the dataset
        :return: The API's response as a Dataset object.
        """
        response = requests.get(
            self.client.api_url + self.uri + '/' + name,
            headers=self.client.headers,
        )
        if response.status_code == 200:
            return Dataset(self.client, response.json())
        
    def download(self, id):
        """
        Download a dataset by id.

        :param id: The id of the dataset
        :return: The API's response as a Dataset object.
        """
        response = requests.get(
            self.client.api_url + self.uri + '/' + id + '/download',
            headers=self.client.headers,
        )
        if response.status_code == 200:
            resp = response.json()
            url = resp['url']

            data = requests.get(url)
            arr = data.text.split('\n')
            j = [json.loads(i) for i in arr if i != '']
            return j

    
    def create(self, name, content):
        """
        Create a dataset.

        :param name: The name of the dataset
        :param data: The data to be uploaded
        :return: The API's response as a Dataset object.
        """

        # TODO: Validate messages format


        # check name is kebab case
        if not is_kebab_case(name):
            raise ValueError('Dataset name must be alphanumeric, separated by hyphens, and end with a letter or number.')
        
        response = requests.post(
            self.client.api_url + self.uri + '/create',
            headers=self.client.headers,
            json={'name': name}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # get signerd url and put data
            url = data['url']
            dataset = data['dataset']
            jsonl = "\n".join([json.dumps(x) for x in content])
            response = requests.put(url, data=jsonl)
            #send completeq request
            complete = requests.post(
                self.client.api_url + self.uri + "/"+ dataset['id'] +  '/complete',
                headers=self.client.headers,
                json={'datasetString': dataset['datasetString']}
            )
            if complete.status_code == 200:
                
                
                response = requests.get(
                    self.client.api_url + self.uri + "/"+ dataset['datasetString'],
                    headers=self.client.headers,
                    json={'datasetString': dataset['datasetString']}
                )
                
                return Dataset(self.client, response.json())
            else:
                print(complete.json())
                raise ValueError('Error uploading dataset')
            
        else:
            print(response.json())
            raise ValueError(response.json()['message'])
    
class Dataset:
    def __init__(self, client, data):
        self.client = client
        self.uri='/v1/datasets'
        self.id = data['id']
        self.name = data['name']
        self.dataset_string = data['datasetString']
        self.team_id = data['teamId']
        self.size = data['size']
        self.tokens = data['tokens']
        self.examples = data['examples']
        self.status = data['status']
        self.created_at = data['createdAt']

    def __repr__(self):
        return f'<Dataset {self.dataset_string}>'

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'datasetString': self.dataset_string,
            'teamId': self.team_id,
            'size': self.size,
            'tokens': self.tokens,
            'examples': self.examples,
            'status': self.status,
            'createdAt': self.created_at
        }
    
    def download(self):
        """
        Download a dataset by id.

        :param id: The id of the dataset
        :return: The API's response as a Dataset object.
        """
        response = requests.get(
            self.client.api_url + self.uri + '/' + self.dataset_string + '/download',
            headers=self.client.headers,
        )
        if response.status_code == 200:
            resp = response.json()
            print(resp)
            url = resp['signedUrl']

            data = requests.get(url)
            arr = data.text.split('\n')
            j = [json.loads(i) for i in arr if i != '']
            return j
        else:
            print(response.json())
        
    def delete(self):
        """
        Delete a dataset by id.

        :param id: The id of the dataset
        :return: The API's response as a Dataset object.
        """
        response = requests.delete(
            self.client.api_url + self.uri + '/' + self.id ,
            headers=self.client.headers,
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(response.json())
