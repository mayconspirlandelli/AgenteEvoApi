import requests
import json
import time

# Configurações do teste
WEBHOOK_URL = "http://localhost:5006/webhook"

def test_webhook_connection():
    """Testa se a rota base do Flask está respondendo."""
    print("1. Testando conexão com a aplicação Flask...")
    try:
        response = requests.get("http://localhost:5006/")
        if response.status_code == 200:
            print(f"Sucesso! Resposta: {response.json()['message']}")
            return True
        else:
            print(f"Erro: O servidor respondeu com status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("Erro: Não foi possível conectar ao servidor. Certifique-se de que o Flask está rodando (python src/receber_whatsapp.py)")
    return False

def simulate_whatsapp_message():
    """Simula um payload JSON enviado pela EvolutionAPI quando uma mensagem é recebida."""
    print("\n2. Simulando envio de mensagem do WhatsApp via Webhook...")
    
    # Payload similar ao enviado pela Evolution API
    payload = {
        "event": "messages.upsert",
        "instance": "EvoApiMac",
        "data": {
            "key": {
                "remoteJid": "5562999999999@s.whatsapp.net",
                "fromMe": False,
                "id": "ABC123456789"
            },
            "pushName": "Usuario Teste",
            "message": {
                "conversation": "Olá! Este é um teste do meu Webhook!"
            },
            "messageType": "conversation",
            "messageTimestamp": int(time.time()),
            "source": "ios"
        }
    }

    try:
        headers = {
            'Content-Type': 'application/json',
            'ngrok-skip-browser-warning': 'true'
        }
        response = requests.post(WEBHOOK_URL, data=json.dumps(payload), headers=headers)
        
        if response.status_code == 200:
            print("Sucesso! Webhook processou a mensagem simulada.")
            print(f"Resposta do Servidor: {response.json()}")
        else:
            print(f"Falha: O servidor retornou {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"Erro ao enviar POST: {e}")

if __name__ == "__main__":
    if test_webhook_connection():
        simulate_whatsapp_message()
