import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import os
import sys

# Adiciona APENAS o diretório 'src/telegram' ao sys.path para importar agent_telegram diretamente.
# NÃO adicionamos 'src' ao path, pois isso faria o Python encontrar a pasta 'src/telegram'
# ao resolver 'from telegram import ...', conflitando com a biblioteca python-telegram-bot instalada.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'telegram')))

from agent_telegram import TelegramBotSandeco

class TestTelegramBotSandeco(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        # Mock do ambiente para o TOKEN
        self.env_patcher = patch.dict(os.environ, {"TELEGRAM_API_TOKEN": "123456789:ABCDEFGH"})
        self.env_patcher.start()

        # Mock da Application do python-telegram-bot para evitar conexões reais
        self.app_patcher = patch('telegram.ext.Application.builder')
        self.mock_builder = self.app_patcher.start()
        self.mock_app = MagicMock()
        self.mock_builder.return_value.token.return_value.build.return_value = self.mock_app

        # Callbacks de teste
        self.mock_callback = AsyncMock(return_value="Resposta de texto")
        self.mock_callback_foto = AsyncMock(return_value="Resposta de foto")

        # Inicializa o bot
        self.bot = TelegramBotSandeco(
            callback=self.mock_callback,
            callback_foto=self.mock_callback_foto,
            saudacao="Bem-vindo"
        )

    def tearDown(self):
        self.env_patcher.stop()
        self.app_patcher.stop()

    async def test_initialization(self):
        """Testa se o bot é inicializado corretamente."""
        self.assertEqual(self.bot.TOKEN, "123456789:ABCDEFGH")
        self.assertEqual(self.bot.saudacao, "Bem-vindo")
        # Verifica se os handlers foram adicionados (5 no código atual: start, text, photo, video, document)
        self.assertEqual(self.mock_app.add_handler.call_count, 5)

    async def test_start_command(self):
        """Testa o comando /start."""
        mock_update = MagicMock()
        mock_update.effective_user.mention_html.return_value = "@user"
        mock_update.message.reply_html = AsyncMock()
        
        await self.bot.start(mock_update, MagicMock())
        
        mock_update.message.reply_html.assert_called_once()
        args, kwargs = mock_update.message.reply_html.call_args
        self.assertIn("Bem-vindo @user!", args[0])

    async def test_get_message(self):
        """Testa o processamento de mensagens de texto."""
        mock_update = MagicMock()
        mock_update.message.from_user.first_name = "Maycon"
        mock_update.message.text = "Olá bot"
        mock_update.message.reply_text = AsyncMock()

        await self.bot.get_message(mock_update, MagicMock())

        # Verifica se o callback foi chamado com a mensagem e o nome do usuário capitalizado
        self.mock_callback.assert_called_once_with("Olá bot", "Maycon")
        # Verifica se a resposta do callback foi enviada de volta
        mock_update.message.reply_text.assert_called_once_with("Resposta de texto")

    @patch('tempfile.gettempdir', return_value='/tmp')
    async def test_get_photo(self, mock_temp):
        """Testa o processamento de imagens."""
        mock_update = MagicMock()
        mock_photo = MagicMock()
        mock_photo.file_id = "file_id_123"
        mock_update.message.photo = [mock_photo]  # Lista de tamanhos de foto
        mock_update.message.caption = "Legenda da foto"
        mock_update.message.from_user.id = 12345
        mock_update.message.reply_text = AsyncMock()

        mock_file = MagicMock()
        mock_file.download_to_drive = AsyncMock()
        mock_context = MagicMock()
        mock_context.bot.get_file = AsyncMock(return_value=mock_file)

        await self.bot.get_photo(mock_update, mock_context)

        # Verifica se buscou o arquivo e tentou baixar
        mock_context.bot.get_file.assert_called_once_with("file_id_123")
        mock_file.download_to_drive.assert_called_once()
        
        # Verifica se o callback de foto foi acionado
        self.mock_callback_foto.assert_called_once()
        # Verifica se respondeu ao usuário
        mock_update.message.reply_text.assert_called_once_with("Resposta de foto")

if __name__ == "__main__":
    unittest.main()
