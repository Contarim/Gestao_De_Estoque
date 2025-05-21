from flask import Flask, request, jsonify

app = Flask(__name__)

# Estoque na memória
produtos = []
proximo_id = 1

# Rota para listar todos os produtos
@app.route('/produtos', methods=['GET'])
def listar_produtos():
    return jsonify(produtos)

# Rota para obter um produto específico por ID
@app.route('/produtos/<int:id>', methods=['GET'])
def obter_produto(id):
    for produto in produtos:
        if produto['id'] == id:
            return jsonify(produto)
    return jsonify({'error': 'Produto não encontrado'}), 404

# Rota para criar um único produto
@app.route('/produtos', methods=['POST'])
def criar_produto():
    global proximo_id
    dados = request.json
    if not dados:
        return jsonify({'error': 'Dados JSON ausentes ou inválidos'}), 400

    # Adicionar validação básica para 'nome'
    if 'nome' not in dados or not isinstance(dados['nome'], str) or not dados['nome'].strip():
        return jsonify({'error': 'Campo "nome" é obrigatório e deve ser uma string não vazia'}), 400

    produto = {
        'id': proximo_id,
        'nome': dados['nome'],
        'quantidade': dados.get('quantidade', 0),
        'preco': dados.get('preco', 0.0)
    }
    produtos.append(produto)
    proximo_id += 1
    return jsonify(produto), 201

# Rota para CRIAR MÚLTIPLOS PRODUTOS (BULK INSERT)
@app.route('/produtos/bulk', methods=['POST'])
def criar_varios_produtos():
    global proximo_id
    dados = request.json

    if not isinstance(dados, list):
        return jsonify({'error': 'Requisição deve ser um array de produtos'}), 400

    produtos_adicionados = []
    erros = []

    for item_produto in dados:
        if not isinstance(item_produto, dict):
            erros.append({'error': 'Item no array não é um objeto JSON válido', 'item': item_produto})
            continue

        # Validação básica para 'nome' em cada item
        if 'nome' not in item_produto or not isinstance(item_produto['nome'], str) or not item_produto['nome'].strip():
            erros.append({'error': 'Campo "nome" é obrigatório e deve ser uma string não vazia para um dos produtos', 'item': item_produto})
            continue

        produto = {
            'id': proximo_id,
            'nome': item_produto['nome'],
            'quantidade': item_produto.get('quantidade', 0),
            'preco': item_produto.get('preco', 0.0)
        }
        produtos.append(produto)
        produtos_adicionados.append(produto)
        proximo_id += 1

    if erros:
        # Se houver erros, você pode decidir se quer retornar 200 com os erros
        # e os produtos adicionados, ou 400 se algum erro impede a operação.
        # Aqui, vamos retornar 200 com informações sobre o que foi adicionado e o que falhou.
        return jsonify({
            'message': f'{len(produtos_adicionados)} produtos adicionados com sucesso.',
            'added_products': produtos_adicionados,
            'errors': erros
        }), 200 # ou 400 se você quiser falhar totalmente em caso de qualquer erro
    else:
        return jsonify(produtos_adicionados), 201 # Retorna 201 Created para todos os produtos adicionados com sucesso

# Atualizar produto
@app.route('/produtos/<int:id>', methods=['PUT'])
def atualizar_produto(id):
    dados = request.json
    if not dados:
        return jsonify({'error': 'Dados JSON ausentes ou inválidos'}), 400

    for produto in produtos:
        if produto['id'] == id:
            produto['nome'] = dados.get('nome', produto['nome'])
            produto['quantidade'] = dados.get('quantidade', produto['quantidade'])
            produto['preco'] = dados.get('preco', produto['preco'])
            return jsonify(produto)
    return jsonify({'error': 'Produto não encontrado'}), 404

# Deletar produto
@app.route('/produtos/<int:id>', methods=['DELETE'])
def deletar_produto(id):
    global produtos
    tamanho_antes = len(produtos)
    produtos = [p for p in produtos if p['id'] != id]
    if len(produtos) < tamanho_antes:
        return jsonify({'message': 'Produto deletado'}), 200
    return jsonify({'error': 'Produto não encontrado'}), 404


if __name__ == '__main__':
    app.run(debug=True)