from pathlib import Path


class SpedError(Exception):
    pass


class ArquivoInvalido(SpedError):
    def __init__(self, arquivo: str) -> None:
        nome_arquivo = Path(arquivo).name
        self._message = f'o arquivo {nome_arquivo} não é um Sped FIscal válido.'

    def __repr__(self) -> str:
        return self._message

    def __str__(self) -> str:
        return self._message


class TamanhoRegistroInvalido(SpedError):
    pass


class LinhaRegistroInvalida(SpedError):
    pass


class ValorCampoInvalido(SpedError):
    def __init__(self, campo: str, valor: str) -> None:
        self._campo = campo
        self._valor = valor
        self._message = f'O valor {self._valor} não é um valor valido para o campo {self._campo}.'

    def __repr__(self) -> str:
        return self._message

    def __str__(self) -> str:
        return self._message
