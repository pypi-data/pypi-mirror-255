from argparse import ArgumentParser
from os.path import join

from dramatist.drama.Act import Act
from dramatist.core.Dramatist import Dramatist
import asyncio
import json

from dramatist.core.DramatistParseException import DramatistParseException
from dramatist.drama.Scene import Scene

from requests.exceptions import RequestException


def __json_encoder_drama(obj):
    if isinstance(obj, (Act, Scene)):
        result_dict = obj.__dict__
        return result_dict

    return obj.__dict__


async def main():
    argument_parser = ArgumentParser()

    argument_parser.add_argument('--drama-path', dest='drama_path',
                                 help='Path to the drama xml file', required=False)
    argument_parser.add_argument('--corpus-name', dest='corpus_name',
                                 help='Name of the corpus', required=False)
    argument_parser.add_argument('--play-name', dest='play_name', help='Name of the play', required=False)
    argument_parser.add_argument('--play-id', dest='play_id', help='ID of the play', required=False)
    argument_parser.add_argument('--output-type', choices=['json', 'plain', 'structure'],
                                 dest="output_type", default="text", help="The output type")
    argument_parser.add_argument('--output-folder-path', dest="output_folder_path",
                                 help="The output folder path. If this option is set the output will be saved to a file"
                                      " created in the specified folder")

    args = argument_parser.parse_args()
    drama_path = args.drama_path
    corpus_name = args.corpus_name
    play_name = args.play_name
    play_id = args.play_id
    output_type = args.output_type
    output_folder_path = args.output_folder_path

    if not drama_path and not corpus_name and not play_name and not play_id:
        argument_parser.error('--drama-path or --corpus-name and --play-name or --play-id must be set')
    if drama_path and (corpus_name or play_name or play_id):
        argument_parser.error('only --drama-path or (--corpus-name and --play-name) or --play-id can be used at a time')
    elif play_id and (drama_path or corpus_name or play_name):
        argument_parser.error('only --drama-path or (--corpus-name and --play-name) or --play-id can be used at a time')
    elif (corpus_name and not play_name) or (play_name and not corpus_name):
        argument_parser.error('--corpus-name and --play-name have both to be set together')

    dramatist = Dramatist()

    try:
        if drama_path:
            drama = dramatist.from_file(drama_path)
        elif play_id:
            drama = await dramatist.from_api_by_id(play_id)
        else:
            drama = await dramatist.from_api_by_name(corpus_name, play_name)
    except RequestException as e:
        print(f'Could not load drama: {e}')
    except DramatistParseException as e:
        print(f'Could not parse drama: {e}')
    else:
        if drama:
            output_string = ''
            file_type = ''

            if output_type == 'text':
                output_string = drama.get_text()
                file_type = 'txt'
            elif output_type == 'json':
                output_string = json.dumps(drama, default=__json_encoder_drama)
                file_type = 'json'
            elif output_type == 'structure':
                output_string = drama.get_structure()
                file_type = 'txt'

            if output_folder_path:
                with open(join(output_folder_path, f'{drama.title}.{file_type}'), 'w', encoding='utf-8') as output_file:
                    output_file.write(output_string)
            else:
                print(output_string)
        else:
            print('Could not load drama')


def launch():
    asyncio.run(main())


if __name__ == '__main__':
    launch()
