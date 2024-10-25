import logging
from typing import List
from mutagen.id3._frames import TIT2, TPE1, TALB, TRCK
from mutagen.id3 import ID3, ID3NoHeaderError

logger = logging.getLogger(__name__)


def split_text(text: str, max_chars: int, language: str) -> List[str]:
    """
    Split the input text into chunks based on the specified language and character limit.
    Args:
        text (str): The text to split.
        max_chars (int): Maximum characters allowed per chunk.
        language (str): Language code to determine splitting strategy.
    
    Returns:
        List[str]: List of text chunks.
    """
    # Use language-specific strategy for splitting
    if language.startswith("zh"):  # Chinese-specific strategy
        chunks = split_chinese_text(text, max_chars)
    else:  # Default word-based splitting
        chunks = split_word_based_text(text, max_chars)

    log_chunks(chunks)
    return chunks


def split_chinese_text(text: str, max_chars: int) -> List[str]:
    """
    Split Chinese text by characters, taking care of special characters.
    Args:
        text (str): Chinese text to split.
        max_chars (int): Maximum characters allowed per chunk.
    
    Returns:
        List[str]: List of text chunks.
    """
    chunks = []
    current_chunk = ""
    for char in text:
        if len(current_chunk) + 1 <= max_chars or is_special_char(char):
            current_chunk += char
        else:
            chunks.append(current_chunk)
            current_chunk = char
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


def split_word_based_text(text: str, max_chars: int) -> List[str]:
    """
    Split text by words, ensuring chunks do not exceed the character limit.
    Args:
        text (str): Text to split.
        max_chars (int): Maximum characters allowed per chunk.
    
    Returns:
        List[str]: List of text chunks.
    """
    chunks = []
    current_chunk = ""
    words = text.split()

    for word in words:
        # Adjust for spaces between words when appending
        space_length = 1 if current_chunk else 0
        if len(current_chunk) + len(word) + space_length <= max_chars:
            current_chunk += (" " if current_chunk else "") + word
        else:
            chunks.append(current_chunk)
            current_chunk = word
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


def log_chunks(chunks: List[str]) -> None:
    """
    Log the generated text chunks for debugging purposes.
    Args:
        chunks (List[str]): List of text chunks to log.
    """
    logger.info(f"Split text into {len(chunks)} chunks")
    for i, chunk in enumerate(chunks, 1):
        logger.info(f"Chunk {i}: {chunk[:50]}...")  # Log the first 50 characters of each chunk


def set_audio_tags(output_file: str, audio_tags) -> None:
    """
    Set ID3 tags for an audio file based on the provided audio tags.
    Args:
        output_file (str): Path to the audio file.
        audio_tags: Object containing title, author, book title, and track index.
    """
    try:
        tags = get_or_create_tags(output_file)
        add_audio_tag_fields(tags, audio_tags)
        tags.save(output_file)
    except Exception as e:
        logger.error(f"Error while setting audio tags: {e}, {output_file}")
        raise e


def get_or_create_tags(output_file: str) -> ID3:
    """
    Retrieve existing ID3 tags or create new ones if not found.
    Args:
        output_file (str): Path to the audio file.
    
    Returns:
        ID3: ID3 tag object.
    """
    try:
        tags = ID3(output_file)
        logger.debug(f"tags: {tags}")
    except ID3NoHeaderError:
        logger.debug(f"No ID3 header found for {output_file}. Creating new tags.")
        tags = ID3()
    return tags


def add_audio_tag_fields(tags: ID3, audio_tags) -> None:
    """
    Add the necessary fields to the ID3 tags.
    Args:
        tags (ID3): The ID3 tags object.
        audio_tags: Object containing the audio tag fields to add.
    """
    tags.add(TIT2(encoding=3, text=audio_tags.title))
    tags.add(TPE1(encoding=3, text=audio_tags.author))
    tags.add(TALB(encoding=3, text=audio_tags.book_title))
    tags.add(TRCK(encoding=3, text=str(audio_tags.idx)))


def is_special_char(char: str) -> bool:
    """
    Check if the given character is a special character that shouldn't break the text chunk.
    Args:
        char (str): Character to check.
    
    Returns:
        bool: True if the character is special and shouldn't break the chunk, otherwise False.
    """
    ord_char = ord(char)
    special_chars = "。，、？！：；“”‘’（）《》【】…—～·「」『』〈〉〖〗〔〕∶"
    is_special = (33 <= ord_char <= 126) or (char in special_chars)

    logger.debug(f"is_special_char> char={char}, ord={ord_char}, result={is_special}")
    return is_special