# maquina.py
import socket
import platform
import getpass
from datetime import datetime

class Maquina:
    def __init__(self):
        self.hostname = socket.gethostname()
        self.so = platform.system() + " " + platform.release()
        self.usuario = getpass.getuser()
        self.inicio = datetime.now().strftime("%d/%m/%Y %H:%M")

    def mensagem_inicial(self) -> str:
        return (
            f"🚀 Logger iniciado na máquina: **{self.hostname}**\n"
            f"🖥️ SO: {self.so}\n"
            f"👤 Usuário: {self.usuario}\n"
            f"🕒 Iniciado em: {self.inicio}"
        )