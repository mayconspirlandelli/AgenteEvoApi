from flask import Flask, request, jsonify
from message_sandeco import MessageSandeco
from send_sandeco import SendSandeco
import json
import time


app = Flask(__name__)

@app.route("/", methods=['GET'])
def health_check():
    """Rota para verificar se o servidor está online."""
    return jsonify({
        "status": "online",
        "message": "Webhook da EvolutionAPI está rodando!",
        "endpoints": {
            "webhook": "/webhook (POST)"
        }
    }), 200

@app.route("/webhook", methods=['POST'])
@app.route("/messages-upsert", methods=['POST'])
def webhook():
    """
    Endpoint principal para receber notificações da EvolutionAPI.
    Suporta tanto /webhook quanto /messages-upsert.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400

        print(f"\n{'='*40}")
        print(f"📩 NOVA MENSAGEM RECEBIDA às {time.strftime('%H:%M:%S')}")
        print(f"{'='*40}")
        
        # Organiza os dados da mensagem usando a classe MessageSandeco
        msg = MessageSandeco(data)
        
        print(f"👤 Remetente: {msg.phone}")
        print(f"💬 Conteúdo:  {msg.get_text()}")
        print(f"📦 Tipo:      {msg.message_type}")
        print(f"🆔 ID:        {msg.message_id}")
        print(f"{'-'*40}")
        # print("DEBUG - JSON Bruto:", json.dumps(data, indent=2))


        # Opcional: Responder automaticamente (exemplo: ecoar a mensagem)
        # Atenção: Cuidado com loops infinitos se o bot responder a si mesmo!
        if not msg.from_me:
            # print("Enviando resposta automática (eco)...")
            # sender = SendSandeco()
            # sender.textMessage(number=msg.phone, msg=f"Você disse: {msg.get_text()}")
            pass

        return jsonify({"status": "success", "message": "Mensagem processada"}), 200

    except Exception as e:
        print(f"Erro ao processar webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Roda o servidor localmente na porta 5000
    # host='0.0.0.0' permite acesso de outros dispositivos na mesma rede
    print("Iniciando servidor Flask...")
    app.run(host="0.0.0.0", port=5006, debug=True)
