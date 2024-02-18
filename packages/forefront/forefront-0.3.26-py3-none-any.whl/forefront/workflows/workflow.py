from typing import List, Dict, Any
from ..utils import Chat

class Client():
    def complete(self, run_id, messages, model):
        return {
            "completion": {
                "choices": [
                    {
                        "text": "response"
                    }
                ]
            }
        }

class Workflow():
    # Initialize the Workflow class with inputs, steps, and an empty messages list
    def __init__(self, name = None, inputs: List[str] = [], steps: List[Any] = []):
        self.client = Client()
        self.name = name
        self.vars = {}
        self.extractions = {}
        self.inputs = inputs
        self.steps = steps
        self.messages: List[Dict[str, Any]] = []
        self.completion = None

    # Run the workflow with a given prompt
    def run(self, inputs=[]) -> Any:
        run_id = self.__create_workflow_run()

        for i in self.steps:
            self.messages.append(i)
            res = self.client.complete(run_id, self.messages, 'gpt-3.5-turbo')
            
            completion = res["completion"]["choices"][0]["text"]
            self.messages.append(Chat(completion, role="assistant"))

        return {
            "run_id": run_id,
            "inputs": self.inputs,
            "vars": self.vars,
            "extractions": self.extractions,
            "messages": self.messages,
        }
 
    # Static method to create a Workflow instance from a given id
    @staticmethod
    def from_id(id: str):
        wf = Workflow.__load_wf_from_db(id)
        return Workflow(wf.inputs, wf.steps)

    # Save the current workflow with a given name
    @staticmethod
    def save(self, name: str):
        return '123'
    
    # Private method to create a workflow run
    def __create_workflow_run(self):
        return '123'
    
    # Private method to load a workflow from the database using a given id
    def __load_wf_from_db(id: str):
        return {
            "inputs": [ "prompt"],
            "steps": []
        }