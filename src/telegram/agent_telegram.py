import os
import base64
import tempfile
import mimetypes
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()


def _file_to_base64(file_path: str) -> tuple[str, str]:
    """Lê um arquivo do disco e retorna (base64_str, mimetype)."""
    mimetype, _ = mimetypes.guess_type(file_path)
    if not mimetype:
        mimetype = "application/octet-stream"
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return b64, mimetype


class TelegramBotSandeco:
    """
    Bot do Telegram capaz de processar mensagens de texto, imagem, vídeo,
    áudio e documentos, passando o conteúdo (com base64) para um agente de IA
    (ex.: AgenteVerificador) de forma similar ao fluxo do WhatsApp.
    """

    def __init__(self, agente, saudacao: str = "Olá! Seja bem-vindo!"):
        """
        :param agente: Objeto com método `verificar(texto, media_base64, mimetype)`.
                       Ex.: instância de AgenteVerificador.
        :param saudacao: Mensagem exibida ao comando /start.
        """
        self.saudacao = saudacao
        self.agente = agente

        self.TOKEN = os.getenv("TELEGRAM_API_TOKEN")
        if not self.TOKEN:
            raise ValueError("Erro: TELEGRAM_API_TOKEN não foi encontrado no .env")

        # Inicializa a aplicação
        self.application = Application.builder().token(self.TOKEN).build()

        # Handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_message)
        )
        self.application.add_handler(MessageHandler(filters.PHOTO, self.get_photo))
        self.application.add_handler(MessageHandler(filters.VIDEO, self.get_video))
        self.application.add_handler(
            MessageHandler(filters.AUDIO | filters.VOICE, self.get_audio)
        )
        self.application.add_handler(
            MessageHandler(filters.Document.ALL, self.get_file)
        )

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    async def _download_temp(self, file_telegram, suffix: str, user_id: int) -> str:
        """Baixa um arquivo Telegram para um diretório temporário e retorna o caminho."""
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, f"{user_id}_{file_telegram.file_unique_id}{suffix}")
        await file_telegram.download_to_drive(file_path)
        return file_path

    async def _processar_midia(
        self,
        update: Update,
        file_path: str,
        caption: str | None = None,
    ) -> str:
        """Converte o arquivo em base64 e chama o agente verificador."""
        try:
            b64, mimetype = _file_to_base64(file_path)
            texto = caption or ""
            resposta = self.agente.verificar(texto, b64, mimetype)
            return resposta
        except Exception as e:
            return f"Erro ao processar mídia: {e}"
        finally:
            # Remove o arquivo temporário após o uso
            try:
                os.remove(file_path)
            except OSError:
                pass

    # ------------------------------------------------------------------
    # Handlers de comandos
    # ------------------------------------------------------------------

    async def start(self, update: Update, context):
        """Responde ao comando /start com uma mensagem de boas-vindas."""
        user = update.effective_user
        await update.message.reply_html(
            f"{self.saudacao} {user.mention_html()}!",
            reply_markup=ForceReply(selective=True),
        )

    # ------------------------------------------------------------------
    # Handlers de mensagens
    # ------------------------------------------------------------------

    async def get_message(self, update: Update, context):
        """Processa mensagens de texto enviadas pelo usuário."""
        user = update.message.from_user.first_name.capitalize()
        user_message = update.message.text
        print(f"[TEXTO] {user}: {user_message}")

        # Passa apenas texto para o agente (sem mídia)
        resposta = self.agente.verificar(user_message)
        await update.message.reply_text(resposta)

    async def get_photo(self, update: Update, context):
        """Recebe fotos, converte para base64 e aciona o agente verificador."""
        user = update.message.from_user
        caption = update.message.caption or ""
        file_id = update.message.photo[-1].file_id  # Melhor qualidade disponível

        print(f"[FOTO] user={user.id} caption='{caption}'")

        photo_file = await context.bot.get_file(file_id)
        file_path = await self._download_temp(photo_file, ".jpg", user.id)

        resposta = await self._processar_midia(update, file_path, caption)
        await update.message.reply_text(resposta)

    async def get_video(self, update: Update, context):
        """Recebe vídeos, converte para base64 e aciona o agente verificador."""
        user = update.message.from_user
        caption = update.message.caption or ""
        video = update.message.video
        print(f"[VÍDEO] user={user.id} mime={video.mime_type} caption='{caption}'")

        video_file = await context.bot.get_file(video.file_id)

        # Determina extensão pelo mimetype do vídeo
        ext = mimetypes.guess_extension(video.mime_type or "video/mp4") or ".mp4"
        file_path = os.path.join(tempfile.gettempdir(), f"{user.id}_{video.file_unique_id}{ext}")
        await video_file.download_to_drive(file_path)

        resposta = await self._processar_midia(update, file_path, caption)
        await update.message.reply_text(resposta)

    async def get_audio(self, update: Update, context):
        """Recebe áudios (audio ou voice note), converte para base64 e aciona o agente."""
        user = update.message.from_user

        # Telegram diferencia 'audio' (arquivo de música) de 'voice' (nota de voz)
        audio = update.message.audio or update.message.voice
        caption = update.message.caption or ""
        print(f"[ÁUDIO] user={user.id} mime={audio.mime_type}")

        audio_file = await context.bot.get_file(audio.file_id)
        ext = mimetypes.guess_extension(audio.mime_type or "audio/ogg") or ".ogg"
        file_path = os.path.join(tempfile.gettempdir(), f"{user.id}_{audio.file_unique_id}{ext}")
        await audio_file.download_to_drive(file_path)

        resposta = await self._processar_midia(update, file_path, caption)
        await update.message.reply_text(resposta)

    async def get_file(self, update: Update, context):
        """Recebe documentos/arquivos genéricos, converte para base64 e aciona o agente."""
        user = update.message.from_user
        document = update.message.document
        caption = update.message.caption or ""
        print(f"[DOCUMENTO] user={user.id} name={document.file_name} mime={document.mime_type}")

        doc_file = await context.bot.get_file(document.file_id)
        ext = os.path.splitext(document.file_name or "")[-1] or ".bin"
        file_path = os.path.join(tempfile.gettempdir(), f"{user.id}_{document.file_unique_id}{ext}")
        await doc_file.download_to_drive(file_path)

        resposta = await self._processar_midia(update, file_path, caption)
        await update.message.reply_text(resposta)

    # ------------------------------------------------------------------
    # Inicialização
    # ------------------------------------------------------------------

    def run(self):
        """Inicia o bot usando polling."""
        print("🤖 Bot do Sandeco está rodando...")
        self.application.run_polling()


# ------------------------------------------------------------------
# Execução direta (teste)
# ------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    from src.agents.agente_verificador import AgenteVerificador

    agente = AgenteVerificador()
    bot = TelegramBotSandeco(agente=agente, saudacao="Olá! Sou o verificador de notícias.")
    bot.run()
