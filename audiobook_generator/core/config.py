from unittest.mock import MagicMock
from audiobook_generator.config.general_config import GeneralConfig

def get_azure_config():
    args = MagicMock(
        input_file='tests/test.epub',
        output_folder='output',
        preview=False,
        output_text=False,
        log='INFO',
        newline_mode='double',
        chapter_start=1,
        chapter_end=-1,
        title_mode="auto",
        remove_endnotes=False,
        tts='azure',
        language='en-US',
        voice_name='en-US-GuyNeural',
        output_format='audio-24khz-48kbitrate-mono-mp3',
        model_name='',
        break_duration='1250'
    )
    return GeneralConfig(args)


def get_openai_config():
    args = MagicMock(
        input_file='tests/test.epub',
        output_folder='output',
        preview=False,
        output_text=False,
        log='INFO',
        newline_mode='double',
        chapter_start=1,
        chapter_end=-1,
        title_mode="auto",
        remove_endnotes=False,
        tts='openai',
        language='en-US',
        voice_name='echo',
        output_format='mp3',
        model_name='tts-1'
    )
    return GeneralConfig(args)