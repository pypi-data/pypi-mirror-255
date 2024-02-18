from typing import List
from dramatist.drama.Markup import Markup


class SpeechPart:
    TYPE_SPEECH_LINE = 0
    TYPE_SPEECH_P_B = 1
    TYPE_SPEECH_P = 2
    TYPE_STAGE_DIRECTION = 3
    TYPE_STAGE_DIRECTION_INLINE = 4

    _text: str = ''

    def __init__(self, text: str, speech_type: int, markups: List[Markup]):
        self.type = speech_type
        self.tokens: List[str] = list()
        self.length = 0
        self.text = text
        self.markups = markups

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, v: str):
        self._text = v
        self.tokens = v.split(' ')
        self.length = len(self.tokens)

    def __len__(self):
        return self.length
