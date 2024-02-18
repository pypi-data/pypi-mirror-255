
from .chat import Chat
from .datasets import Datasets
from .models import Models
from .fine_tunes import FineTunes
from .pipelines import Pipelines
from .threads import Threads
from .eval_sets import EvalSets


class ForefrontClient:
    def __init__(self, api_key, default_model=None, base_url=None, openai_api_key=None):
        self.api_key = api_key
        self.api_url = base_url if base_url else 'https://api.forefront.ai'  # Replace with your actual API URL
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.openai_api_key  = openai_api_key
        self.default_model = default_model

        self.chat = Chat(self)  # Instantiate Chat class
        self.datasets = Datasets(self)
        self.models = Models(self)
        self.fine_tunes = FineTunes(self)
        self.pipelines = Pipelines(self)
        self.threads = Threads(self)
        self.eval_sets = EvalSets(self)