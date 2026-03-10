import os
from dotenv import load_dotenv
from evolutionapi.client import EvolutionClient
from evolutionapi.models.message import TextMessage, MediaMessage

class SendSandeco:
    """
    Classe para enviar mensagens via WhatsApp usando a EvolutionAPI.
    
    Esta classe encapsula os métodos de envio de mensagens de texto, imagens, PDFs, 
    vídeos e documentos, utilizando as credenciais e configurações definidas no arquivo .env.
    
    Attributes:
        evo_api_token (str): Token de autenticação da API Evolution.
        evo_instance_id (str): ID da instância da Evolution.
        evo_instance_token (str): Token da instância.
        evo_base_url (str): URL base da API Evolution.
        number (str): Número de telefone padrão configurado.
        client (EvolutionClient): Cliente inicializado para comunicação com a API.
    
    Example:
        >>> sender = SendSandeco()
        >>> sender.textMessage("5562981234567", "Olá, mundo!")
    """

    def __init__(self) -> None:
        """
        Inicializa a classe SendSandeco.
        
        Carrega as variáveis de ambiente do arquivo .env e inicializa o cliente
        da EvolutionAPI com as credenciais fornecidas.
        
        Raises:
            Exception: Se as variáveis de ambiente necessárias não estiverem definidas.
        """
        # Carregar variáveis de ambiente
        load_dotenv()
        self.evo_api_token = os.getenv("EVO_API_TOKEN")
        self.evo_instance_id = os.getenv("EVO_INSTANCE_NAME")
        self.evo_instance_token = os.getenv("EVO_INSTANCE_TOKEN")
        self.evo_base_url = os.getenv("EVO_BASE_URL")
        
        # Validar variáveis obrigatórias
        missing_vars = []
        if not self.evo_api_token: missing_vars.append("EVO_API_TOKEN")
        if not self.evo_instance_id: missing_vars.append("EVO_INSTANCE_NAME")
        if not self.evo_instance_token: missing_vars.append("EVO_INSTANCE_TOKEN")
        if not self.evo_base_url: missing_vars.append("EVO_BASE_URL")
        
        if missing_vars:
            raise ValueError(f"As seguintes variáveis de ambiente estão faltando no .env: {', '.join(missing_vars)}")


        
        # Inicializar o cliente Evolution
        self.client = EvolutionClient(
            base_url=self.evo_base_url,
            api_token=self.evo_api_token
        )

    def textMessage(self, number, msg, mentions=[]):
        """
        Envia uma mensagem de texto via WhatsApp.
        
        Args:
            number (str): Número de telefone no formato internacional (ex: 5562981234567).
            msg (str): Texto da mensagem a ser enviada.
            mentions (list, optional): Lista de números a serem mencionados na mensagem. Padrão: [].
        
        Returns:
            dict: Resposta da API contendo informações sobre a mensagem enviada.
        
        Example:
            >>> sender.textMessage("5562981234567", "Olá!", mentions=["5562987654321"])
        """
        text_message = TextMessage(
            number=str(number),
            text=msg,
            mentioned=mentions
        )

        response = self.client.messages.send_text(
            self.evo_instance_id, 
            text_message, 
            self.evo_instance_token
        )
        return response

    def PDF(self, number, pdf_file, caption=""):
        """
        Envia um arquivo PDF via WhatsApp.
        
        Args:
            number (str): Número de telefone no formato internacional.
            pdf_file (str): Caminho completo do arquivo PDF a ser enviado.
            caption (str, optional): Legenda para o arquivo. Padrão: "".
        
        Raises:
            FileNotFoundError: Se o arquivo PDF não for encontrado.
        
        Example:
            >>> sender.PDF("5562981234567", "/caminho/arquivo.pdf", "Documento importante")
        """
        if not os.path.exists(pdf_file):
            raise FileNotFoundError(f"Arquivo '{pdf_file}' não encontrado.")
        
        media_message = MediaMessage(
            number=number,
            mediatype="document",
            mimetype="application/pdf",
            caption=caption,
            fileName=os.path.basename(pdf_file),
            media=""
        )
        
        self.client.messages.send_media(
            self.evo_instance_id, 
            media_message, 
            self.evo_instance_token,
            pdf_file
        )

    def audio(self, number, audio_file):
        """
        Envia um arquivo de áudio via WhatsApp.
        
        Args:
            number (str): Número de telefone no formato internacional.
            audio_file (str): Caminho completo do arquivo de áudio a ser enviado.
        
        Returns:
            str: Mensagem de confirmação "Áudio enviado".
        
        Raises:
            FileNotFoundError: Se o arquivo de áudio não for encontrado.
        
        Example:
            >>> sender.audio("5562981234567", "/caminho/audio.mp3")
            'Áudio enviado'
        """
        if not os.path.exists(audio_file):
            raise FileNotFoundError(f"Arquivo '{audio_file}' não encontrado.")

        audio_message = {
            "number": number,
            "mediatype": "audio",
            "mimetype": "audio/mpeg",
            "caption": ""
        }
            
        self.client.messages.send_whatsapp_audio(
            self.evo_instance_id,
            audio_message,
            self.evo_instance_token,
            audio_file
        )
                    
        return "Áudio enviado"

    def image(self, number, image_file, caption=""):
        """
        Envia uma imagem via WhatsApp.
        
        Args:
            number (str): Número de telefone no formato internacional.
            image_file (str): Caminho completo do arquivo de imagem a ser enviado.
            caption (str, optional): Legenda para a imagem. Padrão: "".
        
        Returns:
            str: Mensagem de confirmação "Imagem enviada".
        
        Raises:
            FileNotFoundError: Se o arquivo de imagem não for encontrado.
        
        Example:
            >>> sender.image("5562981234567", "/caminho/foto.jpg", "Veja esta foto!")
            'Imagem enviada'
        """
        if not os.path.exists(image_file):
            raise FileNotFoundError(f"Arquivo '{image_file}' não encontrado.")

        media_message = MediaMessage(
            number=number,
            mediatype="image",
            mimetype="image/jpeg",
            caption=caption,
            fileName=os.path.basename(image_file),
            media=""
        )

        self.client.messages.send_media(
            self.evo_instance_id, 
            media_message, 
            self.evo_instance_token,
            image_file
        )
        
        return "Imagem enviada"

    def video(self, number, video_file, caption=""):
        """
        Envia um vídeo via WhatsApp.
        
        Args:
            number (str): Número de telefone no formato internacional.
            video_file (str): Caminho completo do arquivo de vídeo a ser enviado.
            caption (str, optional): Legenda para o vídeo. Padrão: "".
        
        Returns:
            str: Mensagem de confirmação "Vídeo enviado".
        
        Raises:
            FileNotFoundError: Se o arquivo de vídeo não for encontrado.
        
        Example:
            >>> sender.video("5562981234567", "/caminho/video.mp4", "Confira este vídeo!")
            'Vídeo enviado'
        """
        if not os.path.exists(video_file):
            raise FileNotFoundError(f"Arquivo '{video_file}' não encontrado.")

        media_message = MediaMessage(
            number=number,
            mediatype="video",
            mimetype="video/mp4",
            caption=caption,
            fileName=os.path.basename(video_file),
            media=""
        )

        self.client.messages.send_media(
            self.evo_instance_id, 
            media_message, 
            self.evo_instance_token,
            video_file
        )
        
        return "Vídeo enviado"

    def document(self, number, document_file, caption=""):
        """
        Envia um documento via WhatsApp.
        
        Args:
            number (str): Número de telefone no formato internacional.
            document_file (str): Caminho completo do arquivo de documento a ser enviado.
            caption (str, optional): Legenda para o documento. Padrão: "".
        
        Returns:
            str: Mensagem de confirmação "Documento enviado".
        
        Raises:
            FileNotFoundError: Se o arquivo de documento não for encontrado.
        
        Example:
            >>> sender.document("5562981234567", "/caminho/doc.docx", "Relatório final")
            'Documento enviado'
        """
        if not os.path.exists(document_file):
            raise FileNotFoundError(f"Arquivo '{document_file}' não encontrado.")

        media_message = MediaMessage(
            number=number,
            mediatype="document",
            mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            caption=caption,
            fileName=os.path.basename(document_file),
            media=""
        )

        self.client.messages.send_media(
            self.evo_instance_id, 
            media_message, 
            self.evo_instance_token,
            document_file
        )
        
        return "Documento enviado"
