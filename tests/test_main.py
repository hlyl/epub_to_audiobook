import pytest
import argparse
from unittest import mock
from audiobook_generator.config.general_config import GeneralConfig
from audiobook_generator.core.audiobook_generator import AudiobookGenerator
from main import parse_arguments, setup_logging, add_edge_tts_args, add_azure_tts_args, add_piper_tts_args


# Mock get_supported_tts_providers at the module level (where it's imported)
@mock.patch("main.get_supported_tts_providers")
@mock.patch("argparse.ArgumentParser.parse_args")
def test_parse_arguments(mock_parse_args, mock_get_supported_tts_providers):
    # Mock the return value of get_supported_tts_providers
    mock_get_supported_tts_providers.return_value = ["azure", "openai"]
    
    # Create a mock argument namespace with all required attributes
    mock_args = argparse.Namespace(
        input_file="test.epub",
        output_folder="output",
        tts="azure",
        log="INFO",
        preview=False,
        no_prompt=False,
        language="en-US",
        newline_mode="double",
        title_mode="auto",
        chapter_start=1,
        chapter_end=-1,
        output_text=False,
        remove_endnotes=False,
        search_and_replace_file="",
        voice_name=None,
        output_format=None,
        model_name=None,
        break_duration="1250",  # Required for Azure TTS
        voice_rate=None,        # Add other TTS-specific arguments
        voice_volume=None,
        voice_pitch=None,
        proxy=None,
        piper_path="piper",
        piper_speaker=0,
        piper_sentence_silence=0.2,
        piper_length_scale=1.0
    )
    
    mock_parse_args.return_value = mock_args
    
    # Call the function
    config = parse_arguments()
    
    # Check that get_supported_tts_providers was called
    mock_get_supported_tts_providers.assert_called()
    
    # Assert the returned config has the correct values
    assert isinstance(config, GeneralConfig)
    assert config.input_file == "test.epub"
    assert config.output_folder == "output"
    assert config.tts == "azure"
    assert config.break_duration == "1250"

# Test the logging setup
@mock.patch("logging.basicConfig")
def test_setup_logging(mock_basicConfig):
    log_level = "DEBUG"
    
    # Call the function
    setup_logging(log_level)
    
    # Check that basicConfig was called with correct parameters
    mock_basicConfig.assert_called_once()
    args, kwargs = mock_basicConfig.call_args
    assert kwargs["level"] == log_level

# Test for add_edge_tts_args
def test_add_edge_tts_args():
    parser = argparse.ArgumentParser()
    add_edge_tts_args(parser)
    
    args = parser.parse_args([])
    
    assert hasattr(args, "voice_rate")
    assert hasattr(args, "voice_volume")
    assert hasattr(args, "voice_pitch")
    assert hasattr(args, "proxy")

# Test for add_azure_tts_args
def test_add_azure_tts_args():
    parser = argparse.ArgumentParser()
    add_azure_tts_args(parser)
    
    args = parser.parse_args([])
    
    assert hasattr(args, "break_duration")
    assert args.break_duration == "1250"  # Default value

# Test for add_piper_tts_args
def test_add_piper_tts_args():
    parser = argparse.ArgumentParser()
    add_piper_tts_args(parser)
    
    args = parser.parse_args([])
    
    assert hasattr(args, "piper_path")
    assert args.piper_path == "piper"  # Default value
    assert hasattr(args, "piper_speaker")
    assert hasattr(args, "piper_sentence_silence")
    assert hasattr(args, "piper_length_scale")

# Test main function (mocking the AudiobookGenerator and argument parsing)
@mock.patch("main.AudiobookGenerator")
@mock.patch("main.parse_arguments")
@mock.patch("main.setup_logging")
def test_main(mock_setup_logging, mock_parse_arguments, mock_audiobook_generator):
    # Mock the parse_arguments function to return a GeneralConfig object
    mock_config = mock.Mock()
    mock_parse_arguments.return_value = mock_config
    
    # Call the main function
    from main import main
    main()
    
    # Assert the correct functions were called
    mock_parse_arguments.assert_called_once()
    mock_setup_logging.assert_called_once_with(mock_config.log)
    mock_audiobook_generator.assert_called_once_with(mock_config)
    mock_audiobook_generator.return_value.run.assert_called_once()

# Additional tests for specific command-line argument combinations

@mock.patch("sys.argv", ['program', 'input_file.epub', 'output_folder', '--tts', 'azure'])
def test_handle_azure_args():
    config = parse_arguments()
    assert config.tts == 'azure'

@mock.patch("sys.argv", ['program', 'input_file.epub', 'output_folder', '--tts', 'openai'])
def test_handle_openai_args():
    config = parse_arguments()
    assert config.tts == 'openai'

@mock.patch("sys.argv", ['program', 'input_file.epub', 'output_folder', '--tts', 'unsupported_tts'])
def test_handle_unsupported_tts():
    with pytest.raises(SystemExit):  # argparse exits with SystemExit on error
        parse_arguments()

@mock.patch("sys.argv", ['program', 'output_folder', '--tts', 'azure'])
def test_handle_missing_input_file():
    with pytest.raises(SystemExit):  # argparse exits with SystemExit on missing arguments
        parse_arguments()

@mock.patch("sys.argv", ['program', 'input_file.epub', 'output_folder', '--log', 'INVALID_LOG_LEVEL'])
def test_handle_invalid_log_level():
    with pytest.raises(SystemExit):  # argparse exits with SystemExit on invalid arguments
        parse_arguments()
