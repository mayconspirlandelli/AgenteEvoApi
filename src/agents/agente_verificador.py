import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

class AgenteVerificador:
    """
    Agente de IA para verificar se uma notícia é fake ou não.
    Usa LangChain e Gemini com prompt few-shot.
    """

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY não encontrada no arquivo .env")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.1-flash-lite-preview",
            google_api_key=self.api_key,
            temperature=0
        )
        self.setup_agent()

    def setup_agent(self):
        # Exemplos para o Few-Shot Prompt
        examples = [
            {
                "input": "URGENTE: Chá de erva-doce cura o coronavírus em 24 horas, dizem especialistas da China!",
                "output": "Esta notícia é INVERIDICA. Não há comprovação científica de que o chá de erva-doce cure o COVID-19. Organizações de saúde como a OMS desmentiram boatos similares."
            },
            {
                "input": "O governo anunciou hoje o novo calendário de pagamentos do Bolsa Família para o mês de abril.",
                "output": "Esta notícia é VERIDICA. O calendário oficial foi divulgado pelos canais do Governo Federal e da Caixa Econômica Federal."
            },
            {
                "input": "Vídeo mostra neve caindo em plena Avenida Paulista em São Paulo nesta tarde de verão!",
                "output": "Esta notícia é INVERIDICA. Não houve registro de neve em São Paulo recentemente, e as condições climáticas de verão tornam isso impossível. O vídeo provavelmente é manipulado ou de outro local/época."
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
                ("system", "Você é um especialista em verificação de fatos (fact-checker). Sua missão é analisar notícias enviadas e determinar se são verdadeiras, falsas (fake) ou imprecisas, fornecendo uma breve explicação baseada em fatos conhecidos."),
                few_shot_prompt,
                ("human", "{input}"),
            ]
        )

        # Chain
        self.chain = self.final_prompt | self.llm

    def verificar(self, noticia: str) -> str:
        """
        Verifica se a notícia é fake ou não.
        """
        try:
            response = self.chain.invoke({"input": noticia})
            content = response.content
            
            # Se o conteúdo for uma lista (comum em versões recentes do Google GenAI), extrai o texto
            if isinstance(content, list):
                text_parts = []
                for part in content:
                    if isinstance(part, dict) and "text" in part:
                        text_parts.append(part["text"])
                    elif isinstance(part, str):
                        text_parts.append(part)
                return "".join(text_parts).strip()
            
            return content.strip()
        except Exception as e:
            return f"Erro ao processar a verificação: {str(e)}"

if __name__ == "__main__":
    # Teste simples
    agente = AgenteVerificador()
    print(agente.verificar("Beber água de 15 em 15 minutos mata o vírus da gripe."))
