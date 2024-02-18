from __future__ import annotations

from kelvin.message.krn import KRNAssetDataStream
from kelvin.message.message import Message
from kelvin.message.msg_type import KMessageTypeData, KMessageTypeParameter


class AssetDataMessage(Message):
    resource: KRNAssetDataStream


class Number(AssetDataMessage):
    _TYPE = KMessageTypeData("number")

    payload: float = 0.0


class String(AssetDataMessage):
    _TYPE = KMessageTypeData("string")

    payload: str = ""


class Boolean(AssetDataMessage):
    _TYPE = KMessageTypeData("boolean")

    payload: bool = False


class NumberParameter(Message):
    _TYPE = KMessageTypeParameter("number")

    payload: float = 0.0


class StringParameter(Message):
    _TYPE = KMessageTypeParameter("string")

    payload: str = ""


class BooleanParameter(Message):
    _TYPE = KMessageTypeParameter("boolean")

    payload: bool = False
