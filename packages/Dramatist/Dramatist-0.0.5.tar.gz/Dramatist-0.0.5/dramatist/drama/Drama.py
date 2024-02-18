from dataclasses import dataclass, field
from typing import List, Tuple

from dramatist.drama.Act import Act
from dramatist.core.DramatistParseException import DramatistParseException
from dramatist.drama.Markup import Markup
from dramatist.drama.Speech import Speech
from dramatist.drama.SpeechPart import SpeechPart
from dramatist.drama.StageDirection import StageDirection


@dataclass
class Drama:
    title: str
    acts: List[Act] = field(default_factory=list)
    trailer: str = ''

    def new_act(self):
        self.acts.append(Act())

    def new_scene(self):
        if len(self.acts) == 0:
            print('Creating dummy act')
            self.new_act()

        self.acts[-1].new_scene()

    def new_speech(self):
        self.acts[-1].new_speech()

    def set_act_title(self, title: str):
        self.acts[-1].title = title

    def set_scene_title(self, title: str):
        self.acts[-1].set_scene_title(title)

    def set_speaker(self, speaker: str):
        self.acts[-1].set_speaker(speaker)

    def add_act_stage_direction(self, stage_direction: str):
        self.acts[-1].add_stage_direction(stage_direction)

    def add_scene_stage_direction(self, stage_direction: str):
        self.acts[-1].add_scene_stage_direction(stage_direction)

    def add_speech(self, speech: str, speech_type: int, markups: List[Markup]):
        self.acts[-1].add_speech(speech, speech_type, markups)

    def set_trailer(self, trailer: str):
        self.trailer = trailer

    @property
    def act_count(self) -> int:
        return len(self.acts)

    @property
    def scene_count(self) -> int:
        return sum([len(x) for x in self.acts])

    def get_text(self) -> str:
        """
        Get the text of the drama.
        :return: The text of the drama.
        """
        text, _ = self.get_text_with_markup()
        return text

    def get_text_with_markup(self) -> Tuple[str, List[Markup]]:
        """
        Get the text of the drama a list of markups.
        :return: A tuple consisting of the drama text and a list of markup objects, i.e. positions of emphasized text,
        speaker names, act and scene titles.
        """
        result = ''
        markups = []

        for act in self.acts:
            if result:
                result += '\n'

            sub_result, sub_markups = act.get_text_with_markup()
            markups.extend(sub_markups)

            result += f'{sub_result}'

        if self.trailer:
            result += f'\n{self.trailer}'

        return result, markups

    def get_structure(self) -> str:
        """
        Get the structure of the drama.
        :return:
        The structure of the drama as a string, for example:
        1. Act (0:500)
        1. Scene (10:50)
        where the numbers in parentheses represent the character start and end positions.
        """
        result = f'Overview: {self.act_count} acts with {self.scene_count} scenes.'

        for act_nr, act in enumerate(self.acts):
            result += f'\n{act_nr+1}. Act ({act.start}:{act.end})'

            for scene_nr, scene in enumerate(act.scenes):
                result += f'\n{scene_nr+1}. Scene ({scene.start}:{scene.end})'

        return result

    def get_text_for_scene(self, act, scene) -> str:
        """
        Get the text for the given scene in the given act.
        :param act: Number of the act
        :param scene: Number of the scene
        :return: The text of the scene
        """
        return self.acts[act-1].get_text_for_scene(scene)

    def get_text_for_scene_in_blocks(self, act, scene, max_length):
        """
        Get a list of text blocks for the given scene in the given act. Blocks that are longer than the given
        maximum length (in words) are split into multiple blocks.
        :param act: The act number
        :param scene: The scene number
        :param max_length: The maximum length in words of a returned text block. Longer blocks will be split.
        :return: A list of text blocks
        """
        return self.acts[act-1].get_text_for_scene_in_blocks(scene, max_length)

    def get_text_for_scene_by_speaker(self, act, scene, max_length):
        """
        Get a list of text blocks by speaker for the given scene in the given act. This means that for every speaker
        change a new text block is created. Blocks that are longer than the given maximum length (in words)
        are split into multiple blocks.
        :param act: The act number
        :param scene: The scene number
        :param max_length: The maximum length of a returned text block. Longer blocks will be split.
        :return: A list of text blocks
        """
        return self.acts[act-1].get_text_for_scene_by_character(scene, max_length)

    def get_scene_act_for_position(self, search_start: int) -> Tuple[int, int]:
        """
        Return a tuple of act and scene number for the given position.
        :param search_start: The character position for which to return the act and scene number
        :return: A tuple of act and scene number
        """
        found_act_nr = -1
        for act_pos, act in enumerate(self.acts):
            act_start, act_end = act.get_range()

            if act_start <= search_start < act_end:
                found_act_nr = act_pos + 1
                for scene_pos, scene in enumerate(act.scenes):
                    scene_start, scene_end = scene.get_range()

                    if scene_start <= search_start < scene_end:
                        return act_pos + 1, scene_pos + 1

        return found_act_nr, -1

    def get_scene_act_for_line(self, line_nr: int) -> Tuple[int, int]:
        """
        Return a tuple of act and scene number for the given line number.
        :param line_nr: A line number
        :return: A tuple of act and scene number
        """
        for act_pos, act in enumerate(self.acts):
            if act.scenes[-1].end_line >= line_nr:
                for scene_pos, scene in enumerate(act.scenes):
                    if scene.start_line <= line_nr <= scene.end_line:
                        return act_pos + 1, scene_pos + 1

        return -1, -1

    def get_scene_act_for_text(self, text_to_search: str) -> Tuple[int, int]:
        """
        Return a tuple of act and scene number in which the given text appears.
        :param text_to_search: The text so search for
        :return: A tuple of act and scene number
        """
        search_string = text_to_search[0:100]
        search_string = (search_string.lower().replace('\n', '').replace('\t', '')
                         .replace(' ', ''))

        drama_text = (self.get_text().lower().replace('\n', '').replace('\t', '')
                      .replace(' ', ''))
        match_cnt = drama_text.count(search_string)

        if match_cnt == 0:
            return -1, -1
        elif match_cnt > 1:
            raise Exception('Act and scene could not be clearly identified!')

        for act_pos, act in enumerate(self.acts):
            for scene_pos, scene in enumerate(act.scenes):
                scene_text = scene.get_text()
                scene_text = (scene_text.lower().replace('\n', '').replace('\t', '')
                              .replace(' ', ''))

                if search_string in scene_text:
                    return act_pos + 1, scene_pos + 1

        return -1, -1

    def get_range_for_scene(self, act: int, scene: int) -> Tuple[int, int]:
        """
        Return a tuple of character start and end position for the given act and scene number.
        :param act: The act number
        :param scene: The scene number
        :return: A tuple of character start and end position
        """
        if act < 1:
            raise ValueError('Act must be greater than 0.')

        if scene < 1:
            raise ValueError('Scene must be greater than 0.')

        return self.acts[act-1].scenes[scene-1].get_range()

    def update_positions(self):
        total_lines = 0
        total_length = 0

        for act in self.acts:
            if act.title:
                act.markup = Markup(total_length, total_length + len(act.title), 'act')
            act.start = total_length
            total_length += act.get_pre_scene_length()
            for scene in act.scenes:
                text = scene.get_text()
                scene.start = total_length
                scene.end = scene.start + len(text)
                scene.start_line = total_lines + 1
                if scene.title:
                    scene.markup = Markup(total_length, total_length + len(scene.title), 'scene')
                    total_length += len(scene.title) + 1

                for scene_part in scene.scene_parts:
                    if isinstance(scene_part, StageDirection):
                        total_length += len(scene_part.text) + 1
                        continue

                    if not isinstance(scene_part, Speech):
                        raise DramatistParseException('Unknown scene part type')

                    scene_part.start_line = total_lines + 1
                    if scene_part.speaker:
                        scene_part.speaker_markup = Markup(total_length, total_length + len(scene_part.speaker),
                                                           'speaker')
                        total_length += len(scene_part.speaker) + 1
                    for speech_part in scene_part.speech_parts:
                        line_count = 0

                        for markup in speech_part.markups:
                            markup.start = total_length + markup.start
                            markup.end = total_length + markup.end

                        if speech_part.type == SpeechPart.TYPE_SPEECH_LINE:
                            line_count += 1
                        elif speech_part.type == SpeechPart.TYPE_SPEECH_P_B:
                            line_count += 1
                        elif speech_part.type == SpeechPart.TYPE_STAGE_DIRECTION:
                            speech_part.markups.append(Markup(total_length, total_length +
                                                              len(speech_part.text), 'stage'))
                        elif speech_part.type == SpeechPart.TYPE_STAGE_DIRECTION_INLINE:
                            speech_part.markups.append(Markup(total_length, total_length +
                                                              len(speech_part.text), 'stage_inline'))

                        scene_part.end_line = total_lines + line_count
                        total_lines += line_count
                        total_length += len(speech_part.text) + 1

                scene.end_line = total_lines
            act.end = total_length - 1

    def __len__(self) -> int:
        return len(self.acts)

    def __str__(self) -> str:
        return self.get_text()
