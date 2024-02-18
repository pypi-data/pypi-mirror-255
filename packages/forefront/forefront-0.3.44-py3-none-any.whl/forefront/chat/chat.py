import requests

base_urls = {
    "forefront": "https://api.forefront.ai",
    "openai": "https://api.openai.com"
}
class Completions:
    def __init__(self, client):
        self.client = client
        self.default_model = client.default_model
        self.uri='/v1/chat/completions'

    def create(self, model=None, messages = [], provider='forefront', **kwargs ):
        """
        Create a completion using the chat API.

        :param messages: A list of message dicts with 'role' and 'content'.
        :param kwargs: Additional parameters for the API (e.g., model, temperature).
        :return: The API's response as JSON.
        """
        m = model if model else self.default_model

        # assert model is present
        assert m is not None, "Model is required."

        # assert messages is present
        assert messages is not None, "Messages are required."

        
        payload = {
            "model": m,
            "messages": messages,
            **kwargs
        }

        # if stream:
        #     return self._create_stream(payload)
        # else:
        base_url = base_urls[provider]
        headers = self.client.headers
        if provider == 'openai':
            headers['Authorization'] = f'Bearer {self.client.openai_api_key}'
        else:
            headers['Authorization'] = f'Bearer {self.client.api_key}'
        return self._create_non_stream(base_url, headers, payload, provider)

    def _create_non_stream(self, base_url,headers, payload, provider):
        # print(provider)
        response = requests.post(
            base_url + self.uri,
            headers=headers,
            json=payload
        )
        if response.status_code == 200:
            resp = response.json()
            # print(resp)
            resp['message'] = resp['choices'][0]['message']
            return Completion(resp)
        else:
            print(response.json())




class Chat:
    def __init__(self, client):
        self.completions = Completions(client)

class Completion:
    def __init__(self, data, type="forefront"):
       
        # if type == "forefront":
        self.choices = [Choice(choice) for choice in data['choices']]
        # elif type == "openai":
        self.choices = [Choice(choice['message']) for choice in data['choices']]
        self.usage = Usage(data['usage']) if 'usage' in data else None
        self.message = data['content'] if 'message' in data else None

class Choice:
    def __init__(self, data):
        # print(data)
        # print('<S>')
        # print(data)
        # print('<E>')
        self.message = {
            'content': data['content'],
            'role': data['role']
        }
        # self.message = {
        #     'content': data['content'],
        #     'role': data['role']
        # }
        # self.content = data['message']['content']
        # self.role = data['role']

class Usage:
    def __init__(self, data):
        self.total_tokens = data['total_tokens']
        self.input_tokens = data.get('input_tokens', 'prompt_tokens')
        self.output_tokens = data.get('output_tokens', 'completion_tokens')
