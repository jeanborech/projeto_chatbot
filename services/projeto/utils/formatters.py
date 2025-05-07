def formatar_clientes(clientes):
    if not clientes:
        return "Nenhum cliente encontrado."
    return "\n\n".join([f'🧾 **{c["nomeEmpresa"]}**\n📞 {c["telefone"]}\n📧 {c["email"]}\n🆔 CNPJ: {c["cnpj"]}' for c in clientes])

def formatar_produtos(produtos):
    if not produtos:
        return "Nenhum produto encontrado."
    return "\n\n".join([f'📦 **{p["codigoProduto"]}**\n📝 {p["descricao"]}\n💰 R$ {p["valorUnitario"]}' for p in produtos])

def formatar_enderecos(enderecos):
    if not enderecos:
        return "Nenhum endereço encontrado."
    return "\n\n".join([f'🏠 {e["rua"]}, {e["numero"]} - {e["bairro"]}, {e["cidade"]}/{e["estado"]}' for e in enderecos])

def formatar_endereco_detalhado(endereco):
    return f"""
    📍 **Endereço Completo:**
    Rua: {endereco['rua']}, {endereco['numero']}
    Bairro: {endereco['bairro']}
    Cidade: {endereco['cidade']}/{endereco['estado']}
    CEP: {endereco['cep']}
    Complemento: {endereco.get('complemento', 'N/A')}
    """
    
def formatar_cliente_detalhado(cliente):
    return f"""
    🧾 **Cliente: {cliente['nomeEmpresa']}**
    📄 CNPJ: {cliente['cnpj']}
    📞 Telefone: {cliente['telefone']}
    📧 E-mail: {cliente['email']}
    📅 Data de Cadastro: {cliente.get('dataCadastro', 'N/A')}
    💼 Segmento: {cliente.get('segmento', 'N/A')}
    """

def formatar_produto_detalhado(produto):
    return f"""
    📦 **Produto: {produto['codigoProduto']}**
    📝 Descrição: {produto['descricao']}
    💰 Valor: R$ {produto['valorUnitario']}
    📊 Estoque: {produto.get('estoqueAtual', 'N/A')}
    🏷️ Categoria: {produto.get('categoria', 'N/A')}
    📦 Fornecedor: {produto.get('fornecedor', 'N/A')}
    """