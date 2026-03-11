from flask import Flask, request, jsonify
import json
import time
import sys
import os

# Adiciona o diretório 'src' ao sys.path para permitir importações absolutas de core e agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.message_sandeco import MessageSandeco
from core.send_sandeco import SendSandeco
from agents.agente_verificador import AgenteVerificador


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

        # Salva mídia se houver
        # dirname(__file__) é src/receber, .. é src
        temp_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'temp')
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        if msg.message_type in [msg.TYPE_IMAGE, msg.TYPE_AUDIO, msg.TYPE_VIDEO]:
            media_bytes = None
            ext = ""
            if msg.message_type == msg.TYPE_IMAGE:
                media_bytes = msg.image_base64_bytes
                ext = msg.image_mimetype.split('/')[-1] if msg.image_mimetype else 'jpg'
            elif msg.message_type == msg.TYPE_AUDIO:
                media_bytes = msg.audio_base64_bytes
                ext = msg.audio_mimetype.split('/')[-1].split(';')[0] if msg.audio_mimetype else 'ogg'
            elif msg.message_type == msg.TYPE_VIDEO:
                media_bytes = msg.video_base64_bytes
                ext = msg.video_mimetype.split('/')[-1] if msg.video_mimetype else 'mp4'

            if media_bytes:
                filename = f"{msg.message_type}_{int(time.time())}.{ext}"
                filepath = os.path.join(temp_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(media_bytes)
                print(f"📁 Mídia salva em: {filepath}")
            else:
                if msg.message_type in [msg.TYPE_IMAGE, msg.TYPE_AUDIO, msg.TYPE_VIDEO]:
                    print(f"⚠️ Mídia detectada ({msg.message_type}), mas base64 (media_bytes) está vazio.")


        # Opcional: Responder automaticamente (exemplo: ecoar a mensagem)
        # Atenção: Cuidado com loops infinitos se o bot responder a si mesmo!
        # Responde automaticamente verificando notícia (Texto, Imagem, Áudio, Vídeo)
        if not msg.from_me:
            msg_text = msg.get_text()
            media_base64 = None
            mimetype = None
            
            # Detecta mídias e extrai base64/mimetype
            if msg.message_type == msg.TYPE_IMAGE:
                media_base64 = msg.image_base64
                mimetype = msg.image_mimetype
            elif msg.message_type == msg.TYPE_AUDIO:
                media_base64 = msg.audio_base64
                mimetype = msg.audio_mimetype
            elif msg.message_type == msg.TYPE_VIDEO:
                media_base64 = msg.video_base64
                mimetype = msg.video_mimetype
            
            if msg_text or msg.message_type in [msg.TYPE_IMAGE, msg.TYPE_AUDIO, msg.TYPE_VIDEO]:
                print(f"🤖 Verificando conteúdo (Tipo: {msg.message_type})")
                
                # Inicializa o agente e verifica a notícia passando o objeto da mensagem
                agent = AgenteVerificador()
                verdict = agent.verificar(msg)
                
                print(f"⚖️ Veredito: {verdict}")
                
                # Envia a resposta de volta pelo WhatsApp
                sender = SendSandeco()
                sender.textMessage(number=msg.phone, msg=verdict)
            else:
                print("⚠️ Mensagem sem conteúdo legível ignorada.")
        
        return jsonify({"status": "success", "message": "Mensagem processada"}), 200

    except Exception as e:
        print(f"Erro ao processar webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # Roda o servidor localmente na porta 5000
    # host='0.0.0.0' permite acesso de outros dispositivos na mesma rede
    print("Iniciando servidor Flask...")
    app.run(host="0.0.0.0", port=5006, debug=True)
