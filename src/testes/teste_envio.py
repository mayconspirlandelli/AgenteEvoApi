# Arquivo de teste para envio de mensagens usando a API do Evo. Este arquivo é usado para testar o envio de mensagens de texto, imagens, PDFs e vídeos para um número de telefone específico usando a API do Evo. Ele utiliza as variáveis de ambiente definidas no arquivo .env para configurar a conexão com a API e o número de telefone do destinatário.

import os
from dotenv import load_dotenv
from evolutionapi.client import EvolutionClient
from evolutionapi.models.message import TextMessage, MediaMessage
from send_sandeco import SendSandeco


load_dotenv() # Carregar as variáveis de ambiente do arquivo .env
evo_api_token = os.getenv("EVO_API_TOKEN")
evo_instance_id = os.getenv("EVO_INSTANCE_NAME")
evo_instance_token = os.getenv("EVO_INSTANCE_TOKEN")   
celular = os.getenv("EVO_PHONE_NUMBER") # Pegando o número de telefone do destinatário a partir da variável de ambiente


client = EvolutionClient(
    base_url=os.getenv("EVO_BASE_URL"),
    api_token=evo_api_token
)

text_message = TextMessage(
    number=celular,
    text="Olá, esta é uma mensagem de teste enviada pelo AgenteEvoApi!"
)

response = client.messages.send_text(
    evo_instance_id,
    text_message,
    evo_instance_token)

print(f"Resposta do envio: {response}")


# Instancia a classe SendSandeco para usar seus métodos de envio de mensagens de mídia (PDF, imagem, vídeo e áudio). A classe SendSandeco é uma classe personalizada que encapsula os métodos de envio de mensagens usando a API do Evo, facilitando o processo de envio de diferentes tipos de mídia para um número de telefone específico. Ela utiliza as credenciais e configurações definidas no arquivo .env para autenticar e configurar a conexão com a API do Evo.
sender = SendSandeco() 

# ENVIAR PDF
pdf_file = os.path.join('src', 'temp','Attention Is All You Need.pdf')

resposta =sender.PDF(number=celular, 
          pdf_file=pdf_file, 
          caption="Attention Is All You Need")

sender.textMessage(number=celular, msg="PDF enviado com sucesso!")
print(f"Resposta do envio: {resposta}")


# ENVIAR IMAGEM
image = os.path.join('src', 'temp','mafalda.png')
resposta = sender.image(number=celular,
            image_file=image,
            caption="Mafalda linda")

sender.textMessage(number=celular, msg="Imagem enviada com sucesso!")
print(f"Resposta do envio: {resposta}")


# Caminho para salvar o vídeo na pasta 'temp'
# Caminho do vídeo dentro da pasta 'temp'

# Enviar o vídeo
video_path = os.path.join('src', 'temp', 'sandeco.mp4')

# Certifique-se de que o arquivo realmente existe
if not os.path.exists(video_path):
   raise FileNotFoundError(f"Arquivo '{video_path}' não encontrado dentro de 'temp'.")


resposta = sender.video(
    number=celular,
    video_file=video_path,  # Arquivo aberto
    caption="Sandeco"  # Legenda do vídeo
)

# Exibir a resposta
sender.textMessage(number=celular, msg="Vídeo enviado com sucesso!")
print(f"Resposta do envio: {resposta}")



# Enviar o audio
audio_path = os.path.join('src', 'temp', 'audio.mp3')
if not os.path.exists(audio_path):
   raise FileNotFoundError(f"Arquivo '{audio_path}' não encontrado dentro de 'temp'.")

resposta = sender.audio(
    number=celular,    
    audio_file=audio_path,  # Arquivo aberto
    caption="Audio de teste"  # Legenda do áudio    
)   
sender.textMessage(number=celular, msg="Áudio enviado com sucesso!")
print(f"Resposta do envio: {resposta}")
