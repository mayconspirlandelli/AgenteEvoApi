import os
from send_sandeco import SendSandeco

sender = SendSandeco()

celular = "5562999999999"
celular = os.getenv("EVO_PHONE_NUMBER") # Pegando o número de telefone do destinatário a partir da variável de ambiente


#sender.textMessage(number=celular,
#                  msg="Digite a mensagem:")


#pdf_file = os.path.join('temp','Attention Is All You Need.pdf')
#sender.PDF(number=celular, 
#           pdf_file=pdf_file, 
#           caption="Attention Is All You Need")

#image = os.path.join('temp','mafalda.png')
#sender.image(number=celular,
#             image_file=image,
#             caption="Mafalda linda")


# Caminho para salvar o vídeo na pasta 'temp'

# Caminho do vídeo dentro da pasta 'temp'


# Certifique-se de que o arquivo realmente existe
#if not os.path.exists(video_path):
#    raise FileNotFoundError(f"Arquivo '{video_path}' não encontrado dentro de 'temp'.")

# Enviar o vídeo
video_path = os.path.join('temp', 'sandeco.mp4')
resposta = sender.video(
    number=celular,
    video_file=video_path,  # Arquivo aberto
    caption="Sandeco"  # Legenda do vídeo
)

# Exibir a resposta
# print(f"Resposta do envio: {resposta}")
