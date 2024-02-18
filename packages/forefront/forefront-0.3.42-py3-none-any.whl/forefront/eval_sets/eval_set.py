
import requests
from tqdm import tqdm
from forefront.utils import AssistantChat
import asyncio
import aiohttp


import json

class EvalSets:
    def __init__(self,client):
        self.client = client
        self.uri='/v1/eval-sets'
    
    def list(self):
        """
        List all eval sets.

        :return: The API's response as EvalSet objects.
        """
        response = requests.get(
            self.client.api_url + self.uri + '/list',
            headers=self.client.headers
        )
        if response.status_code == 200:
            eval_sets = [EvalSet(self.client, d) for d in response.json()]
            return eval_sets
        

    def get(self, id):
        """
        Get an eval set by id.

        :param id: The id of the eval set
        :return: The API's response as an EvalSet object.
        """
        response = requests.get(
            self.client.api_url + self.uri + '/' + id,
            headers=self.client.headers,
        )
        if response.status_code == 200:
            resp = response.json()
            eval_set = EvalSet(self.client, response.json())
            data = requests.get(resp['url'])
            eval_set.set_data(data.text.split('\n'))
            return eval_set
        
        else:
            return response.json()
        
    def create(self, name= None, data=None, description=None, is_public=False):
        """
        Create an eval set.

        :param name: The name of the eval set
        :param data: The data of the eval set
        :param description: The description of the eval set
        :param is_public: Whether the eval set is public
        :return: The API's response as an EvalSet object.
        """
        if name is None:
            raise Exception('name is required')
        if data is None:
            raise Exception('data is required')
        
        if not self._validate_data(data):
            raise Exception('Validation error in data. Ensure data is an array of object. Each object must have steps array where each step has a role (user, assistant, system) and content. Each step can have an option id string and metadata field containing key-value string pairs')


        payload = {
            'name': name,
            'data': data,
            'description': description,
            'isPublic': is_public
        }
        response = requests.post(
            self.client.api_url + self.uri + '/create',
            headers=self.client.headers,
            json=payload
        )
        if response.status_code == 200:
            print(response.json())
            eval_set = EvalSet(self.client, response.json())
            data = requests.get(eval_set.url)
            eval_set.set_data(data.text.split('\n'))
            return eval_set
        else:
            print(response.text)

    # validate data, each item must have steps array where each step has a role (user, assistant, system) and content
    # can have an option id string and metadata record object
    def _validate_data(self,data):
        for item in data:
            if 'steps' not in item:
                raise Exception('steps is required')
            for step in item['steps']:
                if 'role' not in step:
                    raise Exception('role is required')
                #check role is user, assistant or system
                if step['role'] not in ['user', 'assistant', 'system']:
                    raise Exception('role must be user, assistant or system')
                if 'content' not in step:
                    raise Exception('content is required')
                if 'metadata' in step:
                    if not isinstance(step['metadata'], dict):
                        raise Exception('metadata must be a record')
                    
        return True
            
    

class EvalSet:
    def __init__(self, client, data):
        self.client = client
        self.id = data['id']
        self.name = data['fullName']
        self.is_public = data['isPublic']
        self.description = data['description']
        self.created_at = data['createdAt']
        self.metadata = data['metadata']
        
    def set_data(self, data):
        self.data = [EvalItem(self.client,d) for d in data]
        return self

    async def run_eval(
            self,
            start=None,
            end=None,
            model=None,
            temperature=0.5,
            max_tokens=256,
            batch_size=4,
            store_progress=[]
    ):
        runs = store_progress 

        # max batch size is 16
        if batch_size > 16:
            print("Batch size cannot be greater than 16")
            return

        if start is None:
            start = 0
        if end is None:
            end = len(self.data)
       
        pbar = tqdm(total=end-start)  # Initialize tqdm with total number of iterations
        for i in range(start, end, batch_size):
            batch_items = self.data[i:i+batch_size]
            tasks = [item.run(model=model, temperature=temperature, max_tokens=max_tokens) for item in batch_items]
            batch_runs = await asyncio.gather(*tasks)
            runs.extend([{"messages": run} for run in batch_runs])
            pbar.update(batch_size)  # Update tqdm progress bar by batch size
        
        pbar.close()  # Close tqdm progress bar after loop completion
        
        return runs
    
class EvalItem:
    def __init__(self,client, data):
        parsed = json.loads(data)
        self.client = client
        self.id = parsed['id'] if 'id' in parsed else None
        self.metadata = parsed['metadata'] if 'metadata' in parsed else None
        self.steps = [EvalItemStep(s) for s in parsed['steps']] if 'steps' in parsed else []

    async def run(self, model=None, temperature=0.5, max_tokens=256):
        messages = []

        if model is None:
            print("No model provided")
            return

        for step in self.steps:
            messages.append(step.to_json())
            completion = self.client.chat.completions.create(
                messages=messages,
                temperature=temperature,
                model=model,
                max_tokens=max_tokens,
            )
            if completion.message:
                messages.append(AssistantChat(completion.message))
            else:
                print("Error running sequences")
                break
        return messages


class EvalItemStep:
    def __init__(self, data):
        self.role = data['role']
        self.content = data['content']

    def to_json(self):
        return {
            'role': self.role,
            'content': self.content
        }
