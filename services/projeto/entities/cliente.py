from services.api_service import APIService

class ClienteHandler:
    def __init__(self, api_service):
        self.api = api_service
    
    def buscar_todos(self):
        return self.api.get("cliente")
    
    def buscar_por_nome(self, nome):
        clientes = self.buscar_todos()
        return [c for c in clientes if nome.lower() in c["nomeEmpresa"].lower()]
    
    def buscar_nomes(self):
        clientes = self.buscar_todos()
        return [c["nomeEmpresa"] for c in clientes]
    
    def buscar_cnpjs(self):
        clientes = self.buscar_todos()
        return [c["cnpj"] for c in clientes]