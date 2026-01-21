import socket, platform, getpass
from datetime import datetime
import requests
import time

MAIN_ID = "3ecb6ef6-86f4-4075-85a4-6aefe966b4eb"  # substituído pelo launcher

def coletar_info():
    hostname = socket.gethostname()
    so = platform.system() + " " + platform.release()
    usuario = getpass.getuser()
    inicio = datetime.now().strftime("%d/%m/%Y %H:%M")
    return hostname, so, usuario, inicio

def notificar_bot():
    hostname, so, usuario, inicio = coletar_info()
    dados = {
        "main_id": MAIN_ID,
        "hostname": hostname,
        "so": so,
        "usuario": usuario,
        "inicio": inicio
    }

    url = "http://127.0.0.1:5000/report"

    # tenta até 5 vezes com intervalo de 2s
    for tentativa in range(5):
        try:
            requests.post(url, json=dados, timeout=5)
            print(f"[Sucesso] Notificação enviada na tentativa {tentativa+1}")
            break
        except Exception as e:
            print(f"[Tentativa {tentativa+1}] Falha ao notificar bot: {e}")
            time.sleep(2)
    else:
        print("[Aviso] Não foi possível notificar o bot após várias tentativas.")

if __name__ == "__main__":
    # espera alguns segundos antes de tentar (pra dar tempo do Flask subir)
    time.sleep(3)
    notificar_bot()