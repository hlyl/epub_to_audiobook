from unittest import mock
import pytest
from audiobook_generator.config.general_config import GeneralConfig
from audiobook_generator.book_parsers.base_book_parser import (
    get_supported_book_parsers, 
    get_book_parser, 
    BaseBookParser
)

EPUB = "epub"

# Test BaseBookParser interface methods
def test_base_book_parser_methods_raise_not_implemented():
    config = mock.Mock(spec=GeneralConfig)

    # Use pytest.raises to assert that the constructor itself raises NotImplementedError
    with pytest.raises(NotImplementedError):
        # This will trigger validate_config(), which raises NotImplementedError
        BaseBookParser(config)

    # Now, mock the validate_config to avoid immediate NotImplementedError
    with mock.patch.object(BaseBookParser, 'validate_config', return_value=None):
        base_parser = BaseBookParser(config)

        # Ensure get_book raises NotImplementedError
        with pytest.raises(NotImplementedError):
            base_parser.get_book()

        # Ensure get_book_title raises NotImplementedError
        with pytest.raises(NotImplementedError):
            base_parser.get_book_title()

        # Ensure get_book_author raises NotImplementedError
        with pytest.raises(NotImplementedError):
            base_parser.get_book_author()

        # Ensure get_chapters raises NotImplementedError
        with pytest.raises(NotImplementedError):
            base_parser.get_chapters("")

# Test get_supported_book_parsers
def test_get_supported_book_parsers():
    supported_parsers = get_supported_book_parsers()
    assert isinstance(supported_parsers, list)
    assert EPUB in supported_parsers

# Test get_book_parser for EPUB
@mock.patch("audiobook_generator.book_parsers.epub_book_parser.EpubBookParser")
def test_get_book_parser_epub(mock_epub_parser):
    config = mock.Mock(spec=GeneralConfig)
    config.input_file = "test.epub"

    # Call get_book_parser and check that it returns the correct parser
    parser = get_book_parser(config)
    
    mock_epub_parser.assert_called_once_with(config)
    assert parser == mock_epub_parser.return_value

# Test get_book_parser for unsupported format
def test_get_book_parser_unsupported_format():
    config = mock.Mock(spec=GeneralConfig)
    config.input_file = "test.txt"  # Unsupported format

    # Ensure that NotImplementedError is raised for unsupported formats
    with pytest.raises(NotImplementedError):
        get_book_parser(config)
