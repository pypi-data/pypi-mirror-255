from abc import ABC, abstractmethod
from typing import List
from pydantic import BaseModel
from pyspedfiscal.exception import ValorCampoInvalido, LinhaRegistroInvalida, TamanhoRegistroInvalido


class Registro(BaseModel, ABC):
    @classmethod
    def ler_registro(cls, linha: str):
        valores = linha.split("|")[1:-1]

        # Todos os atributos da classe
        campos = list(cls.__fields__.keys())

        # Exclui os atributos com exclude=True
        # Geralmente os filhos
        if cls.__exclude_fields__:
            campos = [
                campo for campo in campos if campo not in cls.__exclude_fields__]

        # Checa o o tamnho do registro
        if len(campos) != len(valores):
            raise TamanhoRegistroInvalido(
                f'Registro com tamanho inválido. \n {linha}')

        valores_dict = dict(list(zip(campos, valores)))

        try:
            return cls(**valores_dict)
        except ValorCampoInvalido as e:
            raise LinhaRegistroInvalida(f'Linha invalida.\n{linha}\n{e}')


class Bloco(BaseModel, ABC):

    @classmethod
    @abstractmethod
    def ler_registros(cls, registros: List[str]):
        pass

    def __setattr__(self, name, value):
        self.__dict__[name] = value
