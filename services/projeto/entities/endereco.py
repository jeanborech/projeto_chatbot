from services.api_service import APIService

class EnderecoHandler:
    def __init__(self, api_service):
        self.api = api_service
    
    def buscar_todos(self):
        return self.api.get("enderecos")
    
    def buscar_por_cidade(self, cidade):
        enderecos = self.buscar_todos()
        return [e for e in enderecos if cidade.lower() in e["cidade"].lower()]