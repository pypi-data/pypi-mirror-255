from dataclasses import dataclass, field
from typing import List, Tuple

from dramatist.core.DramatistParseException import DramatistParseException
from dramatist.drama.Markup import Markup
from dramatist.drama.Scene import Scene
from dramatist.TextBlock import TextBlock


@dataclass
class Act:
    title: str = ''
    epigraph = ''
    scenes: List[Scene] = field(default_factory=list)
    stage_directions: List[str] = field(default_factory=list)
    start: int = 0
    end: int = 0
    markup: Markup = None

    def add_text_to_epigraph(self, text: str):
        if self.epigraph:
            self.epigraph += '\n'
        self.epigraph += text

    def new_scene(self):
        self.scenes.append(Scene())

    def new_speech(self):
        self.scenes[-1].new_speech()

    def set_scene_title(self, title: str):
        self.scenes[-1].title = title

    def set_speaker(self, speaker: str):
        self.scenes[-1].set_speaker(speaker)

    def add_stage_direction(self, stage_direction: str):
        if len(self.scenes) > 0:
            raise DramatistParseException('Stage direction between scenes')

        self.stage_directions.append(stage_direction)

    def add_scene_stage_direction(self, stage_direction: str):
        self.scenes[-1].add_stage_direction(stage_direction)

    def add_speech(self, speech: str, speech_type: int, markups: List[Markup]):
        self.scenes[-1].add_speech(speech, speech_type, markups)

    def get_pre_scene_length(self) -> int:
        length = 0

        if self.title:
            length += len(self.title) + 1

        if self.epigraph:
            length += len(self.epigraph) + 1

        for stage in self.stage_directions:
            length += len(stage) + 1

        return length

    def get_text(self) -> str:
        text, _ = self.get_text_with_markup()
        return text

    def get_text_with_markup(self) -> Tuple[str, List[Markup]]:
        result = ''
        markups = []

        if self.markup:
            markups.append(self.markup)

        # dummy acts do not have a title
        if self.title:
            result = f'{self.title}'

        if self.epigraph:
            result += f'\n{self.epigraph}'

        for stage in self.stage_directions:
            result += f'\n{stage}'

        for scene in self.scenes:
            if result:
                result += '\n'

            sub_text, sub_markups = scene.get_text_with_markup()
            markups.extend(sub_markups)
            result += f'{sub_text}'

        return result, markups

    def get_text_for_scene(self, scene) -> str:
        return self.scenes[scene-1].get_text()

    def get_text_for_scene_in_blocks(self, scene: int, max_length: int) -> List[TextBlock]:
        return self.scenes[scene-1].get_text_in_blocks(max_length)

    def get_text_for_scene_by_character(self, scene: int, max_length: int):
        return self.scenes[scene-1].get_text_by_character(max_length)

    def get_range(self) -> Tuple[int, int]:
        return self.start, self.end

    def __len__(self):
        return len(self.scenes)
