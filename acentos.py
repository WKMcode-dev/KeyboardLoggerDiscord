import unicodedata

class CatalogoAcentos:
    def __init__(self):
        self._mapa = {
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

    def normalizar(self, texto: str) -> str:
        """Aplica normalização Unicode e substitui combinações por acentos."""
        texto = unicodedata.normalize("NFC", texto)
        for combo, acento in self._mapa.items():
            texto = texto.replace(combo, acento)
        return texto

    def adicionar(self, combo: str, acento: str):
        """Permite adicionar novos combos futuramente."""
        self._mapa[combo] = acento

    def remover(self, combo: str):
        """Permite remover combos do catálogo."""
        if combo in self._mapa:
            del self._mapa[combo]