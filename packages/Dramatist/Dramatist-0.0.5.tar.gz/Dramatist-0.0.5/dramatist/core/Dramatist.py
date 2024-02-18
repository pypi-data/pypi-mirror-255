from dramatist.drama.Drama import Drama
import re
import requests
import asyncio

from dramatist.core.DramatistParseException import DramatistParseException
from dramatist.drama.Markup import Markup
from dramatist.drama.SpeechPart import SpeechPart
import xml.etree.ElementTree as ElementTree


class Dramatist:

    def from_file(self, file_path):
        """
        Load a drama from the given file path.
        :param file_path: The file path to the xml file
        :return: A drama
        """
        xml_root = ElementTree.parse(file_path).getroot()
        return self.__create_drama(xml_root)

    def from_api_by_name(self, corpus_name, play_name):
        """
        Load a drama from the DraCor API.
        :param corpus_name: The DraCor corpus name
        :param play_name: The DraCor play name
        :return: A drama
        """
        task1 = asyncio.create_task(
            self.__load_play_from_api(corpus_name, play_name)
        )

        return task1

    def from_api_by_id(self, play_id):
        """
        Load a drama from the DraCor API.
        :param play_id: The DraCor play id
        :return: A drama
        """
        task1 = asyncio.create_task(
            self.__load_play_from_id(play_id)
        )

        return task1

    async def __load_play_from_id(self, play_id):
        play_info = await self.__load_info(play_id)

        if play_info:
            corpus_name = play_info['corpus']
            play_name = play_info['name']
            return await self.__load_play_from_api(corpus_name, play_name)
        else:
            return None

    async def __load_info(self, play_id):
        headers = {
            'Accept': 'application/json'
        }

        response = requests.get(f'https://dracor.org/api/v1/id/{play_id}', headers=headers)
        if response.status_code == 200:
            result_json = response.json()
            return result_json
        else:
            return None

    async def __load_play_from_api(self, corpus_name, play_name):
        headers = {
            'Accept': 'application/xml'
        }

        response = requests.get(f'https://dracor.org/api/v1/corpora/{corpus_name}/plays/{play_name}/tei',
                                headers=headers)

        if response.status_code == 200:
            xml_root = ElementTree.fromstring(response.text)
            return self.__create_drama(xml_root)
        else:
            return None

    def __create_drama(self, xml_root):
        ns = self.__get_namespace(xml_root)
        body_content = xml_root.find(f'.//{ns}body')
        drama_name = xml_root.find(f'.//{ns}title[@type="main"]').text
        drama = Drama(drama_name)
        self.__get_text_from_element(ns, body_content, False, True, [], None, drama,
                                     False)
        drama.update_positions()
        return drama

    def __get_namespace(self, element):
        m = re.match(r'\{.*}', element.tag)
        return m.group(0) if m else ''

    def __get_text_from_element(self, ns, element, use_tail, is_first_act, stack, sibling_tag, drama, first_child):
        new_beginning = False
        result = ''
        markups = []

        if element.tag == f'{ns}div':
            div_type = element.attrib.get('type')
            stack.append(div_type)
        else:
            stack.append(element.tag.removeprefix(ns))

        if element.tag == f'{ns}div':
            div_type = element.attrib.get('type')

            if div_type == 'prologue':
                drama.new_act()

            if div_type == 'act':
                drama.new_act()

            if div_type == 'scene':
                drama.new_scene()

        if element.tag == f'{ns}sp':
            drama.new_speech()

        # There can be speech with only stage instruction before
        if element.tag == f'{ns}lg' and 'sp' not in stack:
            drama.new_speech()

        if element.tag == f'{ns}l' or element.tag == f'{ns}head' or element.tag == f'{ns}stage':
            new_beginning = True

        # emph is ignored, so we need a space
        if element.tag == f'{ns}emph':
            if not first_child:
                result += ' '
            markups.append(Markup(0, -1, 'emph'))

        if element.tag == f'{ns}pb':
            if not first_child:
                result += ' '

        if element.text:
            text = element.text
            if text:
                cleaned_text = self.__clean_text(text)
                if cleaned_text:
                    new_beginning = False
                    result += cleaned_text

        sub_sibling_tag = None
        is_first = True
        for e_pos, text in enumerate(element):
            is_first_child_at_start = False

            if is_first:
                if 'p' == stack[-1] and not result:
                    is_first_child_at_start = True
                elif new_beginning:
                    is_first_child_at_start = True

            if 'p' in stack and 'p' == stack[-1]:
                if result:
                    if is_first:
                        drama.add_speech(result.strip(), SpeechPart.TYPE_SPEECH_P_B, markups)
                        markups = []
                    else:
                        drama.add_speech(result.strip(), SpeechPart.TYPE_SPEECH_P, markups)
                        markups = []

                    result = ''

            inner_text, is_first_act, sub_sibling_tag, new_markups = (
                self.__get_text_from_element(ns, text, True, is_first_act, stack, sub_sibling_tag, drama,
                                             is_first_child_at_start))

            for nm in new_markups:
                if result:
                    nm.start = nm.start + len(result) + 1
                    nm.end = nm.end + len(result) + 1
                else:
                    nm.start = nm.start
                    nm.end = nm.end

            markups.extend(new_markups)
            result += inner_text
            is_first = False

        if 'emph' == stack[-1]:
            length = len(result.strip())
            markups[-1].end = length

        if 'l' in stack and 'l' == stack[-1]:
            if 'epigraph' in stack:
                drama.acts[-1].add_text_to_epigraph(result.strip())
            else:
                drama.add_speech(result.strip(), SpeechPart.TYPE_SPEECH_LINE, markups)
                markups = []

            result = ''

        # there can be quotes
        if 'bibl' == stack[-1]:
            drama.acts[-1].add_text_to_epigraph(result.strip())
            result = ''

        if 'p' in stack and 'p' == stack[-1] and 'sp' in stack:
            if result:
                if sub_sibling_tag:
                    drama.add_speech(result.strip(), SpeechPart.TYPE_SPEECH_P, markups)
                    markups = []
                else:
                    drama.add_speech(result.strip(), SpeechPart.TYPE_SPEECH_P_B, markups)
                    markups = []

            result = ''

        if 'speaker' in stack:
            drama.set_speaker(result)
            result = ''

        if 'stage' in stack and 'stage' == stack[-1]:
            if 'p' in stack:
                if first_child:
                    drama.add_speech(result.strip(), SpeechPart.TYPE_STAGE_DIRECTION, markups)
                    markups = []
                else:
                    drama.add_speech(result.strip(), SpeechPart.TYPE_STAGE_DIRECTION_INLINE, markups)
                    markups = []
                result = ''
            elif 'sp' in stack:
                if (sibling_tag == 'lg' or sibling_tag == 'l' or sibling_tag == 'head' or sibling_tag == 'stage' or
                        sibling_tag == 'p'):
                    drama.add_speech(result.strip(), SpeechPart.TYPE_STAGE_DIRECTION, markups)
                    markups = []
                    result = ''
                else:
                    drama.add_speech(result.strip(), SpeechPart.TYPE_STAGE_DIRECTION_INLINE, markups)
                    markups = []
                    result = ''
            elif 'scene' in stack:
                drama.add_scene_stage_direction(result)
            elif 'act' in stack:
                drama.add_act_stage_direction(result)
            elif 'prologue' in stack:
                drama.add_act_stage_direction(result)
            else:
                raise DramatistParseException('Unknown stage case')

        if 'scene' in stack and 'head' in stack and 'head' == stack[-1]:
            drama.set_scene_title(result)
            result = ''
        elif 'prologue' in stack and 'head' in stack and 'head' == stack[-1]:
            drama.set_act_title(result)
            result = ''
        elif 'act' in stack and 'head' in stack and 'head' == stack[-1]:
            drama.set_act_title(result)
            result = ''

        if 'trailer' in stack:
            drama.set_trailer(result)
            result = ''

        if use_tail and element.tail:
            text = element.tail
            if text:
                if 'p' in stack and 'stage' == stack[-1]:
                    result += ' '

                if 'emph' in stack:
                    result += ' '

                result += self.__clean_text(text)
                result = result.rstrip(' ')

        last_tag = stack.pop()

        return result, is_first_act, last_tag, markups

    def __clean_text(self, text):
        result = re.sub(" +", " ", text, flags=re.DOTALL)

        if not result == ' ':
            result = text.strip()

        result = re.sub(" *\n *", " ", result, flags=re.DOTALL)
        # result = re.sub(" +", " ", result, flags=re.DOTALL)
        return result
