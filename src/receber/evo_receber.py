
from flask import Flask, request
from message_sandeco import MessageSandeco
from send_sandeco import SendSandeco

app = Flask(__name__)

@app.route("/messages-upsert", methods=['POST'])
def funcao():
    
    data = request.get_json()     

    msg = MessageSandeco(data)
        
    sender = SendSandeco()
    
    sender.textMessage(number=msg.phone, msg=msg.text_message)
    
    return ""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)