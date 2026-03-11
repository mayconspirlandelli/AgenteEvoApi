import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage

class AgenteVerificador:
    """
    Agente de IA para verificar se uma notícia é fake ou não.
    Usa LangChain e Gemini com suporte multi-modal (texto, imagem, áudio, vídeo).
    """

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY não encontrada no arquivo .env")
        
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv("MODEL_GEMINI"),
            google_api_key=self.api_key,
            temperature=0
        )
        self.setup_agent()

    def setup_agent(self):
        # Exemplos para o Few-Shot Prompt
        examples = [
            {
                "input": "URGENTE: Chá de erva-doce cura o coronavírus em 24 horas, dizem especialistas da China!",
                "output": "Esta notícia é INVERÍDICA. Não há comprovação científica de que o chá de erva-doce cure o COVID-19. Organizações de saúde como a OMS desmentiram boatos similares."
            },
            {
                "input": "O governo anunciou hoje o novo calendário de pagamentos do Bolsa Família para o mês de abril.",
                "output": "Esta notícia é VERÍDICA. O calendário oficial foi divulgado pelos canais do Governo Federal e da Caixa Econômica Federal."
            },
            {
                "input": "Vídeo mostra neve caindo em plena Avenida Paulista em São Paulo nesta tarde de verão!",
                "output": "Esta notícia é INVERÍDICA. Não houve registro de neve em São Paulo recentemente, e as condições climáticas de verão tornam isso impossível. O vídeo provavelmente é manipulado ou de outro local/época."
            }
        ]

        # Template para os exemplos
        example_prompt = ChatPromptTemplate.from_messages(
            [
                ("human", "{input}"),
                ("ai", "{output}"),
            ]
        )

        # Configuração do Few-Shot Prompt
        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=examples,
        )

        # Prompt final
        self.final_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Você é um especialista em verificação de fatos (fact-checker). Sua missão é analisar notícias enviadas e determinar se são verdadeiras (VERÍDICAS), falsas (INVERÍDICAS) ou imprecisas, fornecendo uma breve explicação baseada em fatos conhecidos."),
                few_shot_prompt,
                ("human", "{input}"),
            ]
        )

        # Chain
        self.chain = self.final_prompt | self.llm

    def verificar(self, noticia_ou_msg: any, media_base64: str = None, mimetype: str = None) -> str:
        """
        Verifica se a notícia é verídica ou não, suportando texto e mídia.
        Pode receber uma string ou um objeto do tipo MessageSandeco.
        """
        try:
            noticia = ""
            # Se receber o objeto da mensagem, extrai os dados automaticamente
            if hasattr(noticia_ou_msg, 'message_type'):
                msg = noticia_ou_msg
                noticia = msg.get_text()
                if msg.message_type == msg.TYPE_IMAGE:
                    media_base64 = msg.image_base64
                    mimetype = msg.image_mimetype
                elif msg.message_type == msg.TYPE_AUDIO:
                    media_base64 = msg.audio_base64
                    mimetype = msg.audio_mimetype
                elif msg.message_type == msg.TYPE_VIDEO:
                    media_base64 = msg.video_base64
                    mimetype = msg.video_mimetype
            else:
                noticia = noticia_ou_msg

            content = []
            
            # Adiciona o texto se houver
            if noticia:
                content.append({"type": "text", "text": noticia})
 
            # Adiciona a mídia se houver
            if media_base64 and mimetype:
                if mimetype.startswith("image/"):
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:{mimetype};base64,{media_base64}"}
                    })
                else:
                    # Suporte para áudio e vídeo
                    content.append({
                        "type": "media",
                        "mime_type": mimetype,
                        "data": media_base64
                    })
            
            if not content:
                return "Por favor, envie um texto ou mídia para verificação."

            # Se houver mídia, usamos uma abordagem direta para evitar que o LangChain 
            # transforme a lista de conteúdo em uma string ao formatar o prompt.
            if media_base64:
                # Criamos a lista de mensagens manualmente incluindo o prompt do sistema e os exemplos do few-shot
                system_msg = SystemMessage(content="Você é um especialista em verificação de fatos (fact-checker). Sua missão é analisar notícias enviadas (texto, imagem, áudio ou vídeo) e determinar se são verdadeiras (VERÍDICAS), falsas (INVERÍDICAS) ou imprecisas, fornecendo uma explicação baseada em fatos. Se o usuário pedir para descrever uma imagem, faça-o como parte da análise.")
                
                # Exemplos simplificados para contextualizar o modelo multi-modal
                few_shot_messages = [
                    HumanMessage(content="URGENTE: Chá de erva-doce cura o coronavírus em 24 horas!"),
                    SystemMessage(content="Esta notícia é INVERÍDICA. Não há comprovação científica de que o chá de erva-doce cure o COVID-19."),
                    HumanMessage(content="O governo anunciou o novo calendário do Bolsa Família."),
                    SystemMessage(content="Esta notícia é VERÍDICA. O calendário oficial foi divulgado pelos canais do Governo Federal.")
                ]
                
                current_msg = HumanMessage(content=content)
                messages = [system_msg] + few_shot_messages + [current_msg]
                
                response = self.llm.invoke(messages)
            else:
                # Para texto simples, a chain com few-shot prompt funciona perfeitamente
                response = self.chain.invoke({"input": noticia})
            
            res_content = response.content
            
            if isinstance(res_content, list):
                text_parts = []
                for part in res_content:
                    if isinstance(part, dict) and "text" in part:
                        text_parts.append(part["text"])
                    elif isinstance(part, str):
                        text_parts.append(part)
                return "".join(text_parts).strip()
            
            return str(res_content).strip()
        except Exception as e:
            return f"Erro ao processar a verificação: {str(e)}"

if __name__ == "__main__":
    # Teste simples
    agente = AgenteVerificador()
    print(agente.verificar("Lula é o presidente do Brasil."))
