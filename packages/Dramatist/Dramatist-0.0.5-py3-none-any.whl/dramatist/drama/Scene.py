from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import math

from dramatist.core.DramatistParseException import DramatistParseException
from dramatist.drama.Markup import Markup
from dramatist.drama.ScenePart import ScenePart
from dramatist.drama.Speech import Speech
from dramatist.drama.StageDirection import StageDirection
from dramatist.TextBlock import TextBlock


@dataclass
class Scene:
    title: str = ''
    scene_parts: List[ScenePart] = field(default_factory=list)
    start: int = 0
    end: int = 0
    start_line: int = 0
    end_line: int = 0
    markup: Markup = None

    def new_speech(self):
        self.scene_parts.append(Speech())

    def set_speaker(self, speaker: str):
        latest_block = self.scene_parts[-1]
        if isinstance(latest_block, Speech):
            latest_block.speaker = speaker
        else:
            raise DramatistParseException('Invalid latest block')

    def add_stage_direction(self, stage_direction: str):
        self.scene_parts.append(StageDirection(stage_direction))

    def add_speech(self, text: str, speech_type: int, markups: List[Markup]):
        latest_block = self.scene_parts[-1]
        if isinstance(latest_block, Speech):
            latest_block.add_speech_part(text, speech_type, markups)
        else:
            raise DramatistParseException('Invalid latest block')

    def get_text(self) -> str:
        text, _ = self.get_text_with_markup()
        return text

    def get_text_with_markup(self) -> Tuple[str, List[Markup]]:
        result = f'{self.title}'
        markups = []

        if self.markup:
            markups.append(self.markup)

        for scene_part in self.scene_parts:
            if isinstance(scene_part, StageDirection):
                result += f'\n{scene_part.text}'
            elif isinstance(scene_part, Speech):
                result += f'{scene_part.get_speaker()}{scene_part.get_text()}'
                markups.extend(scene_part.get_markups())

        return result, markups

    def get_text_in_blocks(self, max_length: int) -> List[TextBlock]:
        # Only returns spoken text and stage instructions in between.

        result: List[TextBlock] = []
        current: Optional[TextBlock] = None
        current_length: int = 0
        for scene_block in self.scene_parts:

            if isinstance(scene_block, StageDirection):
                continue
                # stage = scene_block
                #
                # if current:
                #     current.text += f'\n{stage.text}'
                # else:
                #     current = TextBlock(0, 0, stage.text)
                #
                # current_length += len(stage)
            elif isinstance(scene_block, Speech):
                speech = scene_block
                if current_length + len(speech) < max_length:
                    if current:
                        current.text += f'\n{speech.speaker}{speech.get_text()}'
                        current.end_line = speech.end_line
                    else:
                        current = TextBlock(speech.start_line, speech.end_line, f'{speech.speaker}{speech.get_text()}')

                    current_length += len(speech)
                else:
                    if current_length > 0:
                        result.append(current)
                        current = None
                        current_length = 0

                    if len(speech) < max_length:
                        current = TextBlock(speech.start_line, speech.end_line, f'{speech.speaker}{speech.get_text()}')
                        current_length = len(speech)
                    else:
                        factor = (len(speech) // max_length) + 1
                        sub_length = math.ceil(len(speech) / factor)
                        parts = [speech.get_tokens()[i:i + sub_length] for i in range(0, len(speech), sub_length)]

                        # Line numbers are only estimations for now
                        line_count = speech.end_line - speech.start_line + 1
                        lines_per_part = line_count // factor
                        line_start = speech.start_line

                        for pos, p in enumerate(parts):
                            text = ' '.join(p)

                            if pos == 0:
                                result.append(TextBlock(line_start, line_start + lines_per_part, f'{speech.speaker} {text}'))
                            else:
                                result.append(TextBlock(line_start, line_start + lines_per_part, text))

                            line_start += lines_per_part

        if current_length > 0:
            result.append(current)

        return result

    # TODO: return text block
    def get_text_by_character(self, max_length: int):
        result = []

        for scene_block in self.scene_parts:
            if isinstance(scene_block, Speech):
                speech = scene_block

                if len(speech) < max_length:
                    result.append((speech.start_line, speech.end_line, f'{speech.speaker}{speech.get_text()}'))
                else:
                    factor = (len(speech) // max_length) + 1
                    sub_length = math.ceil(len(speech) / factor)
                    parts = [speech.get_tokens()[i:i + sub_length] for i in range(0, len(speech), sub_length)]

                    # Line numbers are only estimations for now
                    line_count = speech.end_line - speech.start_line + 1
                    lines_per_part = line_count // factor
                    line_start = speech.start_line

                    for pos, p in enumerate(parts):
                        text = ' '.join(p)

                        if pos == 0:
                            result.append((line_start, line_start + lines_per_part, f'{speech.speaker}{text}'))
                        else:
                            result.append((line_start, line_start + lines_per_part, text))

                        line_start += lines_per_part

        return result

    def get_range(self) -> Tuple[int, int]:
        return self.start, self.end

    def get_line_range(self) -> Tuple[int, int]:
        return self.start_line, self.end_line

    def __len__(self):
        return len(self.scene_parts)
