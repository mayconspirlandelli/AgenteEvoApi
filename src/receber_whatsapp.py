from flask import Flask, request
from message_sandeco import MessageSandeco
from send_sandeco import SendSandeco

app = Flask(__name__)

@app.route("/messages-upsert", methods=['POST'])
def webhook():

    try:
        data = request.get_json()        
        msg = MessageSandeco(data)    
        print("Mensagem recebida:", data)

        send = SendSandeco()
        send.textMessage(number=msg.phone,
                            msg=msg.text_message)



        print(f"Mensagem recebida de {msg.phone}: {msg.text_message}")           

        # Filtrar apenas mensagens contendo a palavra-chave 'help'
        if msg.text_message and 'help' in msg.text_message.lower():
            send = SendSandeco()
            send.textMessage(number=msg.phone,
                             msg=msg.text_message)

    except:
        print("Erro")
    
        
    return ""
        

if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=5000, debug=True)
    app.run(host="192.168.0.100", port=5000, debug=True)



