import argparse
import logging

from audiobook_generator.config.general_config import GeneralConfig
from audiobook_generator.core.audiobook_generator import AudiobookGenerator
from audiobook_generator.tts_providers.base_tts_provider import get_supported_tts_providers


def parse_arguments():
    """
    Parse command-line arguments for the audiobook generation script.
    
    Returns:
        GeneralConfig: Parsed arguments wrapped in the GeneralConfig object.
    """
    parser = argparse.ArgumentParser(description="Convert text book to audiobook")

    parser.add_argument("input_file", help="Path to the EPUB file")
    parser.add_argument("output_folder", help="Path to the output folder")

    parser.add_argument(
        "--tts",
        choices=get_supported_tts_providers(),
        default=get_supported_tts_providers()[0],
        help=(
            "Choose TTS provider (default: azure). "
            "When using Azure, set environment variables MS_TTS_KEY and MS_TTS_REGION. "
            "For OpenAI, set OPENAI_API_KEY."
        ),
    )

    parser.add_argument(
        "--log",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Log level (default: INFO)",
    )

    parser.add_argument(
        "--preview",
        action="store_true",
        help=(
            "Enable preview mode. In this mode, the script prints chapter details instead "
            "of converting text to speech."
        ),
    )

    parser.add_argument(
        "--no_prompt",
        action="store_true",
        help=(
            "Suppress confirmation prompt after estimating cloud cost for TTS. "
            "Useful for scripting."
        ),
    )

    parser.add_argument(
        "--language",
        default="en-US",
        help=(
            "Language for the TTS service (default: en-US). "
            "For Chinese texts, use zh-CN, zh-TW, or zh-HK."
        ),
    )

    parser.add_argument(
        "--newline_mode",
        choices=["single", "double", "none"],
        default="double",
        help=(
            "Mode for detecting new paragraphs: 'single' (one newline), "
            "'double' (two newlines), or 'none'. (default: double)"
        ),
    )

    parser.add_argument(
        "--title_mode",
        choices=["auto", "tag_text", "first_few"],
        default="auto",
        help=(
            "Mode for parsing chapter titles: 'tag_text' (use 'title', 'h1', etc.), "
            "'first_few' (use the first 60 characters), or 'auto' (automatic selection)."
        ),
    )

    parser.add_argument(
        "--chapter_start",
        default=1,
        type=int,
        help="Starting chapter index (default: 1).",
    )

    parser.add_argument(
        "--chapter_end",
        default=-1,
        type=int,
        help="Ending chapter index (default: -1, meaning the last chapter).",
    )

    parser.add_argument(
        "--output_text",
        action="store_true",
        help="Enable plain text export for each chapter.",
    )

    parser.add_argument(
        "--remove_endnotes",
        action="store_true",
        help="Remove endnote numbers from sentences (useful for academic texts).",
    )

    parser.add_argument(
        "--search_and_replace_file",
        default="",
        help=(
            "Path to a file containing regex replacements (format: <search>==<replace>). "
            "Useful for fixing pronunciations."
        ),
    )

    parser.add_argument(
        "--voice_name",
        help="Specify voice name based on the TTS provider's settings.",
    )

    parser.add_argument(
        "--output_format",
        help="Output format for the TTS service, based on the provider.",
    )

    parser.add_argument(
        "--model_name",
        help="Specify the neural model name for the TTS provider.",
    )

    add_edge_tts_args(parser)
    add_azure_tts_args(parser)
    add_piper_tts_args(parser)

    args = parser.parse_args()
    return GeneralConfig(args)


def add_edge_tts_args(parser):
    """Add Edge TTS-specific arguments to the parser."""
    edge_group = parser.add_argument_group(title="Edge-specific options")
    edge_group.add_argument(
        "--voice_rate",
        help=(
            "Speaking rate (e.g., -50%% to +100%%). Use the format --arg=value "
            "for negative values."
        ),
    )
    edge_group.add_argument(
        "--voice_volume",
        help=(
            "Volume level (-100%% to +100%%). Use the format --arg=value for "
            "negative values."
        ),
    )
    edge_group.add_argument(
        "--voice_pitch",
        help=(
            "Baseline pitch (e.g., -80Hz, +50Hz). Adjust pitch within 0.5x to 1.5x "
            "the original."
        ),
    )
    edge_group.add_argument(
        "--proxy",
        help="Proxy server for TTS provider (format: http://[user:pass@]proxy:port).",
    )


def add_azure_tts_args(parser):
    """Add Azure-specific arguments to the parser."""
    azure_group = parser.add_argument_group(title="Azure-specific options")
    azure_group.add_argument(
        "--break_duration",
        default="1250",
        help="Pause between sections in milliseconds (default: 1250ms).",
    )


def add_piper_tts_args(parser):
    """Add Piper-specific arguments to the parser."""
    piper_group = parser.add_argument_group(title="Piper-specific options")
    piper_group.add_argument(
        "--piper_path",
        default="piper",
        help="Path to the Piper TTS executable.",
    )
    piper_group.add_argument(
        "--piper_speaker",
        default=0,
        help="Piper speaker ID for multi-speaker models.",
    )
    piper_group.add_argument(
        "--piper_sentence_silence",
        default=0.2,
        help="Seconds of silence after each sentence (default: 0.2s).",
    )
    piper_group.add_argument(
        "--piper_length_scale",
        default=1.0,
        help="Phoneme length scale, affecting speaking rate.",
    )


def setup_logging(log_level: str):
    """
    Setup logging configuration with the specified log level.
    
    Args:
        log_level (str): The log level to use.
    """
    formatter = logging.Formatter(
        "%(asctime)s - %(filename)s:%(lineno)d - %(funcName)s - %(levelname)s - %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logging.basicConfig(level=log_level, handlers=[console_handler])


def main():
    config = parse_arguments()
    setup_logging(config.log)

    AudiobookGenerator(config).run()


if __name__ == "__main__":
    main()
