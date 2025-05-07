from services.api_service import APIService

class ProdutoHandler:
    def __init__(self, api_service):
        self.api = api_service
    
    def buscar_todos(self):
        return self.api.get("produtos")
    
    def buscar_por_codigo(self, codigo):
        produtos = self.buscar_todos()
        return [p for p in produtos if codigo.lower() in p["codigoProduto"].lower()]
    
    def buscar_descricoes(self):
        produtos = self.buscar_todos()
        return [p["descricao"] for p in produtos]
    
    def buscar_com_valores(self):
        produtos = self.buscar_todos()
        return [f'{p["descricao"]}: R$ {p["valorUnitario"]}' for p in produtos]