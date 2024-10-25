import pytest
from unittest.mock import MagicMock, patch, call
from mutagen.id3 import ID3, ID3NoHeaderError
from audiobook_generator.core.utils import (
    split_text, 
    split_chinese_text, 
    split_word_based_text, 
    set_audio_tags, 
    is_special_char,
    get_or_create_tags, 
    add_audio_tag_fields
)

# Mock logger to avoid unnecessary logs during testing
@pytest.fixture(autouse=True)
def mock_logger():
    with patch("audiobook_generator.core.utils.logger") as mock_log:
        yield mock_log

# Test for split_text function
@pytest.mark.parametrize(
    "text, max_chars, language, expected_chunks",
    [
        ("这是一个测试句子", 3, "zh-CN", ["这是一", "个测试", "句子"]),
        ("This is a test sentence.", 10, "en", ["This is a", "test", "sentence."]),
        ("Short sentence.", 5, "en", ["Short", "sentence."]),
        ("", 10, "en", []),
        ("特殊符号。测试", 3, "zh-CN", ["特殊符", "号。测", "试"]),
    ]
)
def test_split_text(mock_logger, text, max_chars, language, expected_chunks):
    result = split_text(text, max_chars, language)
    assert result == expected_chunks
    mock_logger.info.assert_called()

# Test for split_chinese_text function
@pytest.mark.parametrize(
    "text, max_chars, expected_chunks",
    [
        ("这是一个测试句子", 3, ["这是一", "个测试", "句子"]),
        ("特殊符号。测试", 3, ["特殊符", "号。测", "试"]),
    ]
)
def test_split_chinese_text(mock_logger, text, max_chars, expected_chunks):
    result = split_chinese_text(text, max_chars)
    assert result == expected_chunks
    
    # Assert that the logger was called twice for special characters
    assert mock_logger.debug.call_count == 2

    # Set expected logger calls depending on the input
    if text == "这是一个测试句子":
        calls = [
            call('is_special_char> char=个, ord=20010, result=False'),
            call('is_special_char> char=句, ord=21477, result=False')
        ]
    elif text == "特殊符号。测试":
        calls = [
            call('is_special_char> char=号, ord=21495, result=False'),
            call('is_special_char> char=试, ord=35797, result=False')
        ]
    else:
        calls = []

    mock_logger.debug.assert_has_calls(calls, any_order=True)









# Test for split_word_based_text function
@pytest.mark.parametrize(
    "text, max_chars, expected_chunks",
    [
        ("This is a test sentence.", 10, ["This is a", "test", "sentence."]),
        ("Short sentence.", 5, ["Short", "sentence."]),
    ]
)
def test_split_word_based_text(mock_logger, text, max_chars, expected_chunks):
    result = split_word_based_text(text, max_chars)
    assert result == expected_chunks
    mock_logger.debug.assert_not_called()

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

# Test for get_or_create_tags function with and without header error
@patch("audiobook_generator.core.utils.ID3")
def test_get_or_create_tags(mock_ID3, mock_logger):
    mock_tags = MagicMock()

    # First, simulate successful ID3 tag fetching
    mock_ID3.return_value = mock_tags
    result = get_or_create_tags("output.mp3")
    assert result == mock_tags
    mock_logger.debug.assert_called_once()

    # Now, simulate the ID3NoHeaderError on the first call, and success on the second
    mock_ID3.side_effect = [ID3NoHeaderError, mock_tags]
    mock_ID3.reset_mock()
    mock_logger.reset_mock()

    result = get_or_create_tags("output.mp3")
    # Instead of checking for isinstance, we check that the mock was returned
    assert result == mock_tags  # Ensure the mock object is returned
    mock_logger.debug.assert_any_call("No ID3 header found for output.mp3. Creating new tags.")


# Test for add_audio_tag_fields
@patch("audiobook_generator.core.utils.TIT2")
@patch("audiobook_generator.core.utils.TPE1")
@patch("audiobook_generator.core.utils.TALB")
@patch("audiobook_generator.core.utils.TRCK")
def test_add_audio_tag_fields(mock_TRCK, mock_TALB, mock_TPE1, mock_TIT2, mock_logger):
    mock_tags = MagicMock()
    mock_audio_tags = MagicMock()
    mock_audio_tags.title = "Test Title"
    mock_audio_tags.author = "Test Author"
    mock_audio_tags.book_title = "Test Book"
    mock_audio_tags.idx = 1

    add_audio_tag_fields(mock_tags, mock_audio_tags)

    mock_tags.add.assert_has_calls([
        call(mock_TIT2(encoding=3, text="Test Title")),
        call(mock_TPE1(encoding=3, text="Test Author")),
        call(mock_TALB(encoding=3, text="Test Book")),
        call(mock_TRCK(encoding=3, text="1")),
    ])
    mock_logger.debug.assert_not_called()

# Test for set_audio_tags with valid audio tags
@patch("audiobook_generator.core.utils.get_or_create_tags")
@patch("audiobook_generator.core.utils.add_audio_tag_fields")
def test_set_audio_tags(mock_add_audio_tag_fields, mock_get_or_create_tags, mock_logger):
    mock_tags = MagicMock()
    mock_get_or_create_tags.return_value = mock_tags

    mock_audio_tags = MagicMock()
    mock_audio_tags.title = "Test Title"
    mock_audio_tags.author = "Test Author"
    mock_audio_tags.book_title = "Test Book"
    mock_audio_tags.idx = 1

    set_audio_tags("output.mp3", mock_audio_tags)

    mock_get_or_create_tags.assert_called_once_with("output.mp3")
    mock_add_audio_tag_fields.assert_called_once_with(mock_tags, mock_audio_tags)
    mock_tags.save.assert_called_once_with("output.mp3")

# Test for set_audio_tags when an exception occurs
@patch("audiobook_generator.core.utils.get_or_create_tags")
def test_set_audio_tags_exception(mock_get_or_create_tags, mock_logger):
    mock_get_or_create_tags.side_effect = Exception("Unknown Error")

    mock_audio_tags = MagicMock()

    with pytest.raises(Exception, match="Unknown Error"):
        set_audio_tags("output.mp3", mock_audio_tags)

    mock_logger.error.assert_called_once_with("Error while setting audio tags: Unknown Error, output.mp3")

