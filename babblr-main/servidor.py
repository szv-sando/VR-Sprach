from flask import Flask, request, jsonify
import ollama

app = Flask(__name__)

# A nossa "memória" de curtíssimo prazo para a IA lembrar da pergunta
exercicio_atual = ""

# ROTA 1: GERAR O EXERCÍCIO
@app.route('/gerar-exercicio', methods=['POST'])
def gerar_exercicio():
    global exercicio_atual 
    
    dados = request.json
    nivel_do_aluno = dados.get('nivel', 'iniciante')
    
    prompt = f"Você é um professor de alemão estrito. Crie um exercício curto de tradução para um aluno nível {nivel_do_aluno}. Me dê APENAS o exercício escrito em português do Brasil impecável e com ortografia perfeita para o aluno traduzir. Nenhuma explicação extra. REGRA ABSOLUTA: Retorne SOMENTE a frase em português. Não adicione notas, não escreva em inglês, não coloque saudações, não explique nada. Me dê APENAS o exercício. REGRA: VOCÊ ESTÁ PROIBIDO DE CONVERSAR. NÃO DIGA \"Aqui está\". NÃO DÊ SAUDAÇÕES. EXEMPLO DE SAÍDA CORRETA: O cachorro bebe água. EXEMPLO DE SAÍDA ERRADA: Aqui está sua frase: O cachorro bebe água. Gere UM ÚNICO exercício simples em português do Brasil para um teste de nível {nivel_do_aluno}. REGRA ABSOLUTA: NÃO escreva introduções. NÃO escreva \"Aqui está\". NÃO fale sobre ser professor ou sobre regras. Retorne EXATAMENTE APENAS o exercício. Exemplo: Traduza a frase: O menino bebe água."

    resposta_ia = ollama.chat(model='llama3', messages=[
        {'role': 'user', 'content': prompt}
    ])
    
    exercicio_gerado = f"Traduza para o alemão: {resposta_ia['message']['content'].strip()}"
    
    # Salva o exercício na memória do servidor!
    exercicio_atual = exercicio_gerado 
    
    return jsonify({
        "sucesso": True,
        "texto_exercicio": exercicio_gerado
    })

# ROTA 2: AVALIAR A RESPOSTA
@app.route('/avaliar-resposta', methods=['POST'])
def avaliar_resposta():
    global exercicio_atual 
    
    dados = request.json
    resposta_do_aluno = dados.get('resposta', '')
    
    prompt = f"""
    Você é o juiz de um jogo de idiomas (como o Duolingo). 
    A frase original era: "{exercicio_atual}"
    O aluno traduziu para o alemão como: "{resposta_do_aluno}"

    REGRAS DE AVALIAÇÃO:
    1. Ignore erros de letras maiúsculas/minúsculas.
    2. Se a tradução estiver essencialmente correta e aceitável, comece OBRIGATORIAMENTE com a palavra "ACERTOU" ou algo semelhante.
    3. Se a tradução estiver completamente errada ou sem sentido, comece OBRIGATORIAMENTE com a palavra "ERROU" ou algo semelhante.
    4. Depois da primeira palavra, dê uma explicação curta (máximo 2 frases) em português do Brasil, apenas corrigindo eventualmente ou elogiando. Não invente falsas regras.
    5. APENAS corrija UMA VEZ, não crie mais de uma resposta. Seja direto e objetivo. Não dê dicas para o aluno tentar de novo, apenas corrija ou elogie a resposta dada.

    EXEMPLO DE RESPOSTA CORRETA:
    ACERTOU. Muito bem! Lembre-se apenas que em alemão os substantivos começam com maiúscula (Der Lehrer).
    
    Agora avalie a resposta do aluno:
    """
    
    resposta_ia = ollama.chat(model='llama3', messages=[
        {'role': 'user', 'content': prompt}
    ])
    
    feedback_completo = resposta_ia['message']['content'].strip()
    acertou = True if "ACERTOU" in feedback_completo.upper() else False
    
    return jsonify({
        "sucesso": True,
        "acertou": acertou,
        "feedback": feedback_completo
    })

if __name__ == '__main__':
    print("Cérebro Ollama conectado! Servidor VR Sprach rodando na porta 5000...")
    app.run(debug=True, host='0.0.0.0', port=5000)