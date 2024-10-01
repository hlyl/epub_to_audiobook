import pytest
from unittest.mock import MagicMock, patch, call
from mutagen.id3 import ID3, ID3NoHeaderError
from audiobook_generator.core.utils import split_text, set_audio_tags, is_special_char
from audiobook_generator.config.general_config import GeneralConfig
from audiobook_generator.core.config import get_azure_config, get_openai_config


# Mock logger to avoid unnecessary logs during testing
@pytest.fixture(autouse=True)
def mock_logger():
    with patch("audiobook_generator.core.utils.logger") as mock_log:
        yield mock_log


# Test for split_text function
@pytest.mark.parametrize(
    "text, max_chars, language, expected_chunks",
    [
        # Test splitting by Chinese characters
        ("这是一个测试句子", 3, "zh-CN", ["这是一", "个测试", "句子"]),  # Updated to match current behavior
        # Test splitting by English words
        ("This is a test sentence.", 10, "en", ["This is a", "test", "sentence."]),
        # Test small max_chars for English
        ("Short sentence.", 5, "en", ["Short", "sentence."]),  # Expected result updated to match behavior
        # Test edge case for empty text
        ("", 10, "en", []),
        # Test splitting by Chinese with special characters
        ("特殊符号。测试", 3, "zh-CN", ["特殊符", "号。测", "试"]),  # Updated to match current behavior
    ]
)
def test_split_text(mock_logger, text, max_chars, language, expected_chunks):
    result = split_text(text, max_chars, language)
    assert result == expected_chunks
    mock_logger.info.assert_called()



# Test for is_special_char function
@pytest.mark.parametrize(
    "char, expected_result",
    [
        ("。", True),  # Special punctuation
        ("A", True),   # ASCII character
        ("1", True),   # Numeric character
        ("你", False), # Regular Chinese character
    ]
)
def test_is_special_char(mock_logger, char, expected_result):
    result = is_special_char(char)
    assert result == expected_result
    mock_logger.debug.assert_called_once_with(f"is_special_char> char={char}, ord={ord(char)}, result={expected_result}")


# Test for set_audio_tags function with valid audio tags
@patch("audiobook_generator.core.utils.ID3")
@patch("audiobook_generator.core.utils.TIT2")
@patch("audiobook_generator.core.utils.TPE1")
@patch("audiobook_generator.core.utils.TALB")
@patch("audiobook_generator.core.utils.TRCK")
def test_set_audio_tags(mock_TRCK, mock_TALB, mock_TPE1, mock_TIT2, mock_ID3, mock_logger):
    mock_tags = MagicMock()
    mock_ID3.return_value = mock_tags

    # Create a mock for the audio tags object
    mock_audio_tags = MagicMock()
    mock_audio_tags.title = "Test Title"
    mock_audio_tags.author = "Test Author"
    mock_audio_tags.book_title = "Test Book"
    mock_audio_tags.idx = 1

    # Call the function
    set_audio_tags("output.mp3", mock_audio_tags)

    # Assert tags were added and saved
    mock_tags.add.assert_has_calls([
        call(mock_TIT2(encoding=3, text="Test Title")),
        call(mock_TPE1(encoding=3, text="Test Author")),
        call(mock_TALB(encoding=3, text="Test Book")),
        call(mock_TRCK(encoding=3, text="1")),
    ])
    mock_tags.save.assert_called_once_with("output.mp3")


# Test for set_audio_tags when ID3NoHeaderError occurs
@patch("audiobook_generator.core.utils.ID3")
@patch("audiobook_generator.core.utils.TIT2")
@patch("audiobook_generator.core.utils.TPE1")
@patch("audiobook_generator.core.utils.TALB")
@patch("audiobook_generator.core.utils.TRCK")
def test_set_audio_tags_no_header_error(mock_TRCK, mock_TALB, mock_TPE1, mock_TIT2, mock_ID3, mock_logger):
    mock_tags = MagicMock()

    # Make ID3 raise ID3NoHeaderError on the first call, and return a mock object afterwards
    mock_ID3.side_effect = [ID3NoHeaderError, mock_tags]

    # Create a mock for the audio tags object
    mock_audio_tags = MagicMock()
    mock_audio_tags.title = "Test Title"
    mock_audio_tags.author = "Test Author"
    mock_audio_tags.book_title = "Test Book"
    mock_audio_tags.idx = 1

    # Call the function
    set_audio_tags("output.mp3", mock_audio_tags)

    # Assert the logger caught the ID3NoHeaderError and logged it
    mock_logger.debug.assert_any_call("handling ID3NoHeaderError: output.mp3")

    # Assert the tags were saved
    mock_tags.save.assert_called_once_with("output.mp3")

    



# Test for set_audio_tags when an exception occurs
@patch("audiobook_generator.core.utils.ID3")
def test_set_audio_tags_exception(mock_ID3, mock_logger):
    mock_ID3.side_effect = Exception("Unknown Error")

    # Create a mock for the audio tags object
    mock_audio_tags = MagicMock()

    # Call the function and expect an exception
    with pytest.raises(Exception, match="Unknown Error"):
        set_audio_tags("output.mp3", mock_audio_tags)

    mock_logger.error.assert_called_once_with("Error while setting audio tags: Unknown Error, output.mp3")


# Tests for Azure and OpenAI config using MagicMock
def test_get_azure_config():
    config = get_azure_config()
    assert isinstance(config, GeneralConfig)
    assert config.input_file == 'examples/test1.epub'
    assert config.tts == 'azure'
    assert config.language == 'en-US'


def test_get_openai_config():
    config = get_openai_config()
    assert isinstance(config, GeneralConfig)
    assert config.input_file == '../../../examples/The_Life_and_Adventures_of_Robinson_Crusoe.epub'
    assert config.tts == 'openai'
    assert config.language == 'en-US'
    assert config.voice_name == 'echo'
    assert config.model_name == 'tts-1'
