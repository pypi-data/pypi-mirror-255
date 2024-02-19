import logging

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from test_tele.plugins import TgcfMessage, TgcfPlugin
from test_tele.utils import translate


class TgcfSpecial(TgcfPlugin):
    id_ = "special"

    def __init__(self, data):
        self.special = data
        logging.info(self.special)

    async def modify(self, tm: TgcfMessage) -> TgcfMessage:
        if self.special.translate:
            if tm.text:
                tm = await translate(tm)
        
        return tm

    