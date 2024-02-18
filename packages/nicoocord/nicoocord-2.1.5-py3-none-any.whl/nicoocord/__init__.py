from .modules import (
    Embeds,
    ModalIO,
    Colors,
)
from .ext import (
    JsonParser,
    Database
)
from .utils.log import Log
from .utils.ver_check import version
from .bot import Bot

__title__ = "nicoocord"
__author__ = "littxle"
__license__ = "MIT"
__version__ = "2.1.5"


version._check(__version__)
