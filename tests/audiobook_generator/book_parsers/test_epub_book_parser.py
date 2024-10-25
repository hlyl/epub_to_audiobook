import pytest
from unittest import mock
from audiobook_generator.book_parsers.epub_book_parser import EpubBookParser
from audiobook_generator.config.general_config import GeneralConfig
from ebooklib import epub
from audiobook_generator.core.config import get_azure_config, get_openai_config
from audiobook_generator.book_parsers.base_book_parser import (
    get_supported_book_parsers, 
    get_book_parser, 
    BaseBookParser
)

# Mock objects
@pytest.fixture
def mock_config():
    # Create a mock GeneralConfig with the required attributes
    config = mock.Mock(spec=GeneralConfig)
    config.input_file = "test.epub"  # Mock input file
    config.title_mode = "auto"
    config.search_and_replace_file = ""
    return config

@pytest.fixture
def mock_epub_book(mock_config):
    # Create an EpubBookParser with the mock config
    return EpubBookParser(mock_config)

@pytest.fixture
def mock_epub(mock_config):
    # Create a mock EpubBook object
    mock_book = mock.Mock(spec=epub.EpubBook)
    return mock_book


def test_validate_config(mock_config):
    # Invalid file extension
    mock_config.input_file = "invalid.txt"
    with pytest.raises(ValueError, match="Unsupported file format"):
        EpubBookParser(mock_config)
    
    # Valid config
    mock_config.input_file = "test.epub"
    parser = EpubBookParser(mock_config)
    assert parser.config.input_file == "test.epub"

def test_get_book_title(mock_epub_book, mock_epub):
    # Case 1: Book has title metadata
    mock_epub.get_metadata.return_value = [('Test Title', )]
    mock_epub_book.book = mock_epub
    assert mock_epub_book.get_book_title() == 'Test Title'

    # Case 2: Book has no title metadata
    mock_epub.get_metadata.return_value = []
    mock_epub_book.book = mock_epub
    assert mock_epub_book.get_book_title() == 'Untitled'

def test_get_book_author(mock_epub_book, mock_epub):
    # Case 1: Book has author metadata
    mock_epub.get_metadata.return_value = [('Test Author', )]
    mock_epub_book.book = mock_epub
    assert mock_epub_book.get_book_author() == 'Test Author'

    # Case 2: Book has no author metadata
    mock_epub.get_metadata.return_value = []
    mock_epub_book.book = mock_epub
    assert mock_epub_book.get_book_author() == 'Unknown'

def test_get_chapters(mock_epub_book, mock_epub):
    mock_item = mock.Mock()
    mock_item.get_content.return_value = b"<h1>Chapter 1</h1><p>This is the content of the chapter.</p>"

    mock_epub.get_items_of_type.return_value = [mock_item]
    mock_epub_book.book = mock_epub
    mock_epub_book.config.title_mode = "tag_text"

    chapters = mock_epub_book.get_chapters(break_string="MAGIC_BREAK_STRING")

    assert len(chapters) == 1
    assert chapters[0].title == 'Chapter_1'
    assert len(chapters[0].items) > 0

def test_get_search_and_replaces(mock_epub_book, monkeypatch):
    # Mock the open function and simulate reading the search and replace file
    mock_file_content = "word1==replacement1\nword2==replacement2\n"
    monkeypatch.setattr("builtins.open", mock.mock_open(read_data=mock_file_content))
    
    mock_epub_book.config.search_and_replace_file = "replace_file.txt"
    replacements = mock_epub_book.get_search_and_replaces()

    assert len(replacements) == 2
    assert replacements[0]['search'] == "word1"
    assert replacements[0]['replace'] == "replacement1"
    assert replacements[1]['search'] == "word2"
    assert replacements[1]['replace'] == "replacement2"

def test_get_epub_book_parser_with_azure_config():
    config = get_azure_config()  # Use actual config

    # Test real parsing behavior
    parser = get_book_parser(config)
    assert isinstance(parser, EpubBookParser)
    assert parser.get_book_author() == "Henrik Lynge"
    assert parser.get_book_title() == "AudioBook test"
    assert parser._sanitize_title("A", "   ") == "A"
    assert len(parser.get_chapters("   ")) == 4

def test_get_epub_book_parser_with_openAI_config():
    config = get_openai_config()  # Use actual config

    # Test real parsing behavior
    parser = get_book_parser(config)
    assert isinstance(parser, EpubBookParser)
    assert parser.get_book_author() == "Henrik Lynge"
    assert parser.get_book_title() == "AudioBook test"
    assert parser._sanitize_title("A", "   ") == "A"
    assert len(parser.get_chapters("   ")) == 4



