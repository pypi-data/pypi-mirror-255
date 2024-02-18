from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Literal, Union, Optional
from pydantic.fields import ModelField
from pyspedfiscal.exception import ValorCampoInvalido
from enum import Enum


class Campo(ABC):
    @classmethod
    @abstractmethod
    def __get_validators__(cls):
        pass

    @classmethod
    @abstractmethod
    def validate(cls, v, field: ModelField) -> Union[date, Literal['']]:
        pass


class CampoData(date, Campo):
    """ Representa uma data """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field: ModelField) -> Optional[date]:

        campo = field.name

        if isinstance(v, str):
            if v == '':
                return None

            try:
                return datetime.strptime(v, '%d%m%Y').date()
            except ValueError:
                raise ValorCampoInvalido(campo, v)

        elif isinstance(v, date):
            return v
        elif isinstance(v, datetime):
            return v.date()
        else:
            raise ValorCampoInvalido(campo, v)


class CampoDecimal(Decimal, Campo):
    """ Representa um numero decimal """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field: ModelField) -> Optional[Decimal]:

        campo = field.name

        if isinstance(v, (float, Decimal, int)):
            return Decimal(v)

        if isinstance(v, str):
            if v == '':
                return None

            try:
                return Decimal(v.replace(',', '.'))
            except InvalidOperation:
                raise ValorCampoInvalido(campo, v)

        else:
            raise ValorCampoInvalido(campo, v)


class CampoInteiro(int, Campo):
    """ Representa um numero decimal """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field: ModelField) -> Optional[int]:

        campo = field.name

        if isinstance(v, int):
            return v

        if isinstance(v, str):
            if v == '':
                return None

            try:
                return int(v)
            except ValueError:
                raise ValorCampoInvalido(campo, v)

        else:
            raise ValorCampoInvalido(campo, v)


class CampoAlphanumerico(str, Campo):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field: ModelField) -> Optional[None]:
        campo = field.name

        if isinstance(v, str):
            if v == '':
                return None

            return v

        raise ValorCampoInvalido(campo, v)


class CampoEnumerate(str, Enum):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field: ModelField) -> Optional[str]:

        campo = field.name

        if v == '':
            return None

        if v not in list(cls):
            raise ValorCampoInvalido(campo, v)

        return cls(v)


class CampoSerie(CampoAlphanumerico):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field: ModelField) -> Optional[None]:
        if v == '':
            return None

        if v.isnumeric():
            return str(int(v)).zfill(3)

        return v.strip()


class CampoCNPJ(CampoInteiro):
    pass


class CampoCPF(CampoInteiro):
    pass


class CampoCNPJouCPF(CampoInteiro):
    pass


class CampoChaveAcesso(CampoInteiro):
    pass


class OutroCampo(Campo):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, field: ModelField):
        pass
