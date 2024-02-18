import logging
from typing import Any, Dict

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from test_tele.plugin_models import Replace
from test_tele.plugins import TgcfMessage, TgcfPlugin
from test_tele.utils import replace


class TgcfReplace(TgcfPlugin):
    id_ = "replace"

    def __init__(self, data):
        self.replace = data
        logging.info(self.replace)

    def modify(self, tm: TgcfMessage) -> TgcfMessage:
        msg_text: str = tm.text
        if not msg_text:
            return tm
        for original, new in self.replace.text.items():
            msg_text = replace(original, new, msg_text, self.replace.regex)
        tm.text = msg_text
        return tm
