from ollama import Client
from dataclasses import dataclass
from pathlib import Path

@dataclass
class System:
    message: str

    def format(self):
        return {
            'role': 'system',
            'content': self.message
        }
    
@dataclass
class ActivityRequest:
    message: str

    def format(self):
        data =  {
            'role': 'user',
            'content': f"{self.message}"
        }
            
        return data

class OllamaServer:
    def __init__(self):
        self._url = 'http://localhost:11434'
        self._model = 'llama3.1:8b'
        self.client = Client(host=self._url)
        self.sys_message_path = Path('./sys.txt')

        with open(str(self.sys_message_path.absolute()), 'r') as file:
            self.sys = System(message=file.read())

    def pull(self):
        self.client.pull(model=self._model)
    
    def get_answer(self, message: str):
        activity_request = ActivityRequest(message=message)
        response = self.client.chat(model=self._model, messages=[self.sys.format(), activity_request.format()])
        return response.message.content