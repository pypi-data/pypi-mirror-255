"""
gemmail_python package.

Provides a parser for gemmail and gembox files for misfin servers and clients.

Usage
-----
from gemmail_python import GemMail

gemmail = GemMail.parseGemmail_C(text)
gemmail.prependSender(sender_address, sender_blurb)
newGemmailString = gemmail.string_C()
"""

from .gembox import *
from .gemmail import *
from .gemtext import *
