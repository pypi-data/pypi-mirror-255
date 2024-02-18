from typing import List, Dict, Any
import requests
import asyncio
import aiohttp
from tqdm import tqdm

class Pipelines:
    def __init__(self, client):
        self.client = client
        self.default_model = client.default_model
        self.uri = "/v1/pipelines"

    def create(self, name: str):
        response = requests.post(
            self.client.api_url + self.uri + "/create",
            json={"name": name},
             headers=self.client.headers
        )
        if response.status_code == 200:
            return Pipeline(self.client, response.json())
        
    def get_by_id(self, id: str):
        response = requests.get(
            self.client.api_url + self.uri + "/" + id,
             headers=self.client.headers
        )
        if response.status_code == 200:
            return Pipeline(self.client, response.json())
        
    # TODO list
    def list(self):
        response = requests.get(
            self.client.api_url + self.uri + "/list",
             headers=self.client.headers
        )
        if response.status_code == 200:
            return [Pipeline(self.client, x) for x in response.json()]
        else:
            print(response.text)


class Pipeline():
    def __init__(self, client, data, filters = {}):
        self.client = client
        self.default_model = client.default_model
        self.id  = data['id']
        self.name = data['name']
        self.uri = "/v1/pipelines"
        # combine filters if data[filters] exists
        self.filters = Pipeline._combine_filters(filters, data['filters']) if 'filters' in data else filters

    def add(self, messages=None, user_id=None, group_id=None, metadata=None):
        # TODO: Validate messages array
        obj = {
            "messages": messages,
        }
        if user_id:
            obj["userId"] = user_id
        if group_id:
            obj["groupId"] = group_id
        if metadata:
            obj["metadata"] = metadata

        response = requests.post(
            self.client.api_url + self.uri + "/" + self.id + "/add",
            json=obj,
             headers=self.client.headers
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(response.text)
    
    def get_filters(self):
        return self.filters

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "filters": self.filters
        }
    
    def clear_filters(self):
        self.filters = None

    def get_count(self):
        base_url = self.client.api_url + self.uri + "/" + self.id + "/count"
        response = requests.post(
            base_url,
            json=self.filters,
            headers=self.client.headers
        )
        if response.status_code == 200:
            return response.json()['count']
        else:
            print(response.text)

    def create_dataset_from_pipeline(self, name: str):
        url = self.client.api_url + self.uri + "/" + self.id + "/create-dataset"

        response = requests.post(
            url,
            json={"name": name, **self.filters},
             headers=self.client.headers
        )
        return response.json()
    
    def filter_by_user_id(self, userId: str):
        return Pipeline(self.client, self.to_json(), {"userId": userId})
    
    def filter_by_group_id(self, orgId: str):
        return Pipeline(self.client, self.to_json(), {"groupId": orgId})
    
    def filter_by_metadata(self, metadata: Dict[str, Any]):
        return Pipeline(self.client, self.to_json(), {"metadata": metadata})
    

    async def get_samples(self, limit: int = 10):
        base_url = self.client.api_url + self.uri + "/" + self.id + "/samples" 

        response = requests.post(
            base_url,
            json={"limit": limit, **self.filters},
             headers=self.client.headers
        )

        data = response.json()

        urls = [x['url'] for x in data]

        # print('fetching messages')
        messages = await parallel_fetch(urls)
        # print(messages)
        # # TODO: returns the array of items with a url field
        # # need to get the data for message content

        combined = []
        for i in range(len(data)):
            del data[i]['url']
            combined.append({**data[i], "messages": messages[i]})

        return combined


    def _convert_filter_to_query(self,url,filter):
        if filter:
            # if filter is string
            
            url += "?"
            for key, value in filter.items():
                url += key + "=" + value + "&"
            # remove last &
            url = url[:-1]

        return url
    
    def _combine_filters(current_filters, new_filter):
        if current_filters:
            current_filters.update(new_filter)
            return current_filters
        else:
            return new_filter
        
    
async def fetch_json(session, url):
# print(f"Fetching URL: {url}, Type: {type(url)}")  # Debugging print
    if not isinstance(url, str):
        raise ValueError(f"URL must be a string, got {type(url)}: {url}")
    try:
        async with session.get(url, timeout=5) as response:
            return await response.json()
    except Exception as e:
        print(f"Error fetching URL {url}: {e}")
        return None


async def parallel_fetch(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_json(session, url) for url in urls]
        return await asyncio.gather(*tasks)

