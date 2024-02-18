import requests
# import matplotlib.pyplot as plt


class FineTunes:
    def __init__(self, client):
        self.client = client
        self.default_model = client.default_model
        self.uri = "/v1/fine-tunes"

    def list(self):
        """
        List your fine-tuned models

        :return: The API's response as Model objects.
        """
        response = requests.get(
            self.client.api_url + self.uri + "/list", headers=self.client.headers
        )
        if response.status_code == 200:
            return [FineTune(self.client, m) for m in response.json()]

    def get_by_id(self, id):
        """
        Get a fine-tuned model by id

        :param id: The id of the fine-tuned model
        :return: The API's response as a Model object.
        """
        
        # print deprecation wranring
        print("WARNING: get_by_id is deprecated. Use get_by_name instead.")
        response = requests.get(
            self.client.api_url + self.uri + "/" + id,
            headers=self.client.headers,
            params={"id": id},
        )
        if response.status_code == 200:
            return FineTune(self.client, response.json())
        
    def get_by_name(self, id):
        """
        Get a fine-tuned model by id

        :param id: The id of the fine-tuned model
        :return: The API's response as a Model object.
        """
        response = requests.get(
            self.client.api_url + self.uri + "/" + id,
            headers=self.client.headers,
            params={"id": id},
        )
        if response.status_code == 200:
            return FineTune(self.client, response.json())

    def create(
        self,
        name,
        base_model,
        training_dataset,
        validation_dataset=None,
        epochs=1,
        public=True,
        evals=[],
    ):
        """
        Create a fine-tuned model

        :param name: The name of the fine-tuned model

        """
        data = {
            "name": name,
            "baseModel": base_model,
            "public": public,
            "trainingDatasetName": training_dataset,
            "epochs": epochs,
            "evals": evals,
        }

        if validation_dataset:
            data["validationDatasetName"] = validation_dataset
        response = requests.post(
            self.client.api_url + self.uri + "/create",
            headers=self.client.headers,
            json=data,
        )
        if response.status_code == 200:
            model = response.json()
            return FineTune(self.client, model["model"])
        else:
            print(response.json())
            return None

    def get_loss(self, id, plot=False):
        response = requests.get(
            self.client.api_url + self.uri + "/" + id + "/loss",
            headers=self.client.headers,
        )
        if response.status_code == 200:
            if plot:
                return response.json()
                # loss = response.json()
                # # Extract 'step' and 'loss' values
                # steps = [entry['step'] for entry in loss['data']]
                # losses = [entry['loss'] for entry in loss['data']]

                # # Plotting
                # plt.figure(figsize=(10, 6))
                # plt.plot(steps, losses, marker='o') # 'o' to mark each point
                # plt.title('Loss per Step')
                # plt.xlabel('Step')
                # plt.ylabel('Loss')
                # plt.grid(True)
                # plt.show()
            else:
                return response.json()


class FineTune:
    def __init__(self, client, data):
        self.client = client
        self.uri = "/v1/fine-tunes"
        self.id = data["id"]
        self.name = data["name"]
        self.team_id = data["teamId"]
        self.model_string = data["modelString"]
        self.model_type = data["modelType"]
        self.public = data["public"]
        self.license = data["license"]
        self.status = data["status"]
        self.created_at = data["createdAt"]
        # self.readme_url = data['readmeUrl']
        self.batch_size = data["batchSize"]
        self.checkpoints = data["checkpoints"]
        self.completed_at = data["completedAt"]
        self.deleted_at = data["deletedAt"]
        self.epochs = data["epochs"]
        self.iteration = data["iteration"]
        # self.learning_rate = data['learningRate']
        # self.parent_adapter_id = data['parentAdapterId']
        self.parent_model_string = data["parentModelString"]
        self.trained_tokens = data["trainedTokens"]
        self.training_file_id = data["trainingFileId"]
        self.updated_at = data["updatedAt"]
        self.validation_file_id = data["validationFileId"]
        self.validation = ValidationRun(self.client, data["validation"]) if data["validation"] else None
        self.evals = [EvalRun(self.client, e) for e in data["evals"]]
        self.is_export_ready = data["hasBeenExported"]
        
    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "team_id": self.team_id,
            "model_string": self.model_string,
            "model_type": self.model_type,
            "public": self.public,
            "license": self.license,
            "status": self.status,
            "created_at": self.created_at,
            # 'readme_url': self.readme_url,
            "batch_size": self.batch_size,
            "checkpoints": self.checkpoints,
            "completed_at": self.completed_at,
            "deleted_at": self.deleted_at,
            "epochs": self.epochs,
            "iteration": self.iteration,
            # 'learning_rate': self.learning_rate,
            # 'parent_adapter_id': self.parent_adapter_id,
            "parent_model_string": self.parent_model_string,
            "trained_tokens": self.trained_tokens,
            "training_file_id": self.training_file_id,
            "updated_at": self.updated_at,
            "validation_file_id": self.validation_file_id,
            "evals": [e.to_json() for e in self.evals],
            "validation_runs": [v.to_json() for v in self.validation_runs],
            "is_export_ready": self.is_export_ready,
        }

    def get_loss(self, plot=False):
        response = requests.get(
            self.client.api_url + self.uri + "/" + self.model_string + "/loss",
            headers=self.client.headers,
        )
        if response.status_code == 200:
            # if plot:
            #     loss = response.json()
            #     # Extract 'step' and 'loss' values
            #     steps = [entry["step"] for entry in loss["data"]]
            #     losses = [entry["loss"] for entry in loss["data"]]

            #     # Plotting
            #     plt.figure(figsize=(10, 6))
            #     plt.plot(steps, losses, marker="o")  # 'o' to mark each point
            #     plt.title("Loss per Step")
            #     plt.xlabel("Step")
            #     plt.ylabel("Loss")
            #     plt.grid(True)
            #     plt.show()
            # else:
            return response.json()

    def add_tag(self, tag):
        response = requests.post(
            self.client.api_url + self.uri + "/" + self.model_string + "/tag",
            headers=self.client.headers,
            json={"tag": tag},
        )
        if response.status_code == 200:
            return response.json()
        else:
            return response.json()

    def remove_tag(self, tag):
        response = requests.delete(
            self.client.api_url + self.uri + "/" + self.model_string + "/tag",
            headers=self.client.headers,
            json={"tag": tag},
        )
        if response.status_code == 200:
            return response.json()
        else:
            return response.json()

    def set_license(self, license):
        response = requests.put(
            self.client.api_url + self.uri + "/" + self.model_string + "/license",
            headers=self.client.headers,
            json={"license": license},
        )
        if response.status_code == 200:
            return response.json()
        else:
            return response.json()

    def set_readme_url(self, readme_url):
        response = requests.put(
            self.client.api_url + self.uri + "/" + self.model_string + "/url",
            headers=self.client.headers,
            json={"readmeUrl": readme_url},
        )
        if response.status_code == 200:
            return response.json()
        else:
            return response.json()

    def delete(self):
        response = requests.delete(
            self.client.api_url + self.uri + "/" + self.model_string,
            headers=self.client.headers,
        )
        if response.status_code == 200:
            return response.json()
        else:
            return response.json()

    def export(self, email=None):
        """
          Export the fine-tuned model

          :param email: If export is not ready, the email to send the export notification to (optional)
          :return: The API's response as a Model object.
        """
        response = requests.post(
            self.client.api_url + self.uri + "/" + self.model_string + "/export",
            headers=self.client.headers,
            json={"email": email, "modelString": self.model_string},
        )

        return response.json()


class EvalRun:
    def __init__(self, client, data) -> None:
        self.id = data["id"]
        self.status = data["status"]
        self.eval_string = data["evalString"]
        self.model_string = data["modelString"]
        self.score = data["score"]
        self.purpose = data["purpose"]
        self.created_at = data["createdAt"]
        self.client = client
        self.uri = "/v1/eval-runs"

    def to_json(self):
        return {
            "id": self.id,
            "status": self.status,
            "eval_string": self.eval_string,
            "model_string": self.model_string,
            "score": self.score,
            "purpose": self.purpose,
            "created_at": self.created_at,
        }

    def restart(self):
        # if status is not failed then return error
        if self.status != "FAILED":
            return {"error": "Only failed eval runs can be restarted"}

        print(self.client.api_url + self.uri + "/" + self.id + "/restart")

        response = requests.post(
            self.client.api_url + self.uri + "/" + self.id + "/restart",
            headers=self.client.headers,
        )
        if response.status_code == 200:
            return response.json()
        else:
            return response.json()


class ValidationRun:
    def __init__(self, client, data) -> None:
        self.id = data["id"]
        self.team_id = data["teamId"]
        self.model_string = data["modelString"]
        self.status = data["status"]
        self.created_at = data["createdAt"]
        self.uri = "/v1/validation-runs"

    def to_json(self):
        return {
            "id": self.id,
            "team_id": self.team_id,
            "model_string": self.model_string,
            "status": self.status,
            "created_at": self.created_at,   
        }

    # def restart(self):
    #     # if status is not failed then return error
    #     if self.status != "FAILED":
    #         return {"error": "Only failed eval runs can be restarted"}

    #     print(self.client.api_url + self.uri + "/" + self.id + "/restart")

    #     response = requests.post(
    #         self.client.api_url + self.uri + "/" + self.id + "/restart",
    #         headers=self.client.headers,
    #     )
    #     if response.status_code == 200:
    #         return response.json()
    #     else:
    #         return response.json()
