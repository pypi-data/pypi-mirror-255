from dataclasses import dataclass, field
from typing import List

from dramatist.drama.Markup import Markup
from dramatist.drama.ScenePart import ScenePart
from dramatist.drama.SpeechPart import SpeechPart


@dataclass
class Speech(ScenePart):
    start_line: int = -1
    end_line: int = -1
    speaker: str = ''
    speaker_markup: Markup = None
    speech_parts: List[SpeechPart] = field(default_factory=list)

    def get_text(self) -> str:
        result = ''

        for pos, sb in enumerate(self.speech_parts):
            if sb.type == SpeechPart.TYPE_SPEECH_P_B:
                result += '\n'
            elif sb.type == SpeechPart.TYPE_SPEECH_P:
                result += ' '
            elif sb.type == SpeechPart.TYPE_SPEECH_LINE:
                result += '\n'
            elif sb.type == SpeechPart.TYPE_STAGE_DIRECTION:
                result += '\n'
            elif sb.type == SpeechPart.TYPE_STAGE_DIRECTION_INLINE:
                result += ' '

            result += f'{sb.text}'

        return result

    def get_speaker(self) -> str:
        if self.speaker:
            return f'\n{self.speaker}'
        else:
            return ''

    def get_tokens(self):
        result = []
        for sb in self.speech_parts:
            result.extend(sb.tokens)
        return result

    def get_markups(self) -> List[Markup]:
        markups = []

        if self.speaker_markup:
            markups.append(self.speaker_markup)

        for speech_part in self.speech_parts:
            markups.extend(speech_part.markups)

        return markups

    def add_speech_part(self, text: str, speech_type: int, markups: List[Markup]) -> None:
        self.speech_parts.append(SpeechPart(text, speech_type, markups))

    def __len__(self):
        return sum([len(x) for x in self.speech_parts])
