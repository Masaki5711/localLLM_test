"""Semantic text chunker for Japanese documents."""
import re
import logging

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 64


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[dict[str, str | int]]:
    """Split text into semantic chunks.
    
    Priority: heading boundaries > paragraph boundaries > sentence boundaries
    """
    if not text.strip():
        return []

    # Split by headings first
    sections = _split_by_headings(text)

    chunks: list[dict[str, str | int]] = []
    chunk_index = 0

    for section in sections:
        heading = section.get("heading", "")
        body = section.get("body", "")

        # Split section body into paragraphs
        paragraphs = _split_by_paragraphs(body)

        current_chunk: list[str] = []
        current_length = 0

        if heading:
            current_chunk.append(heading)
            current_length += len(heading)

        for para in paragraphs:
            para_len = len(para)

            if current_length + para_len > chunk_size and current_chunk:
                chunk_text_joined = "\n".join(current_chunk)
                chunks.append({
                    "text": chunk_text_joined,
                    "chunk_index": chunk_index,
                    "heading": heading,
                    "char_count": len(chunk_text_joined),
                })
                chunk_index += 1

                # Overlap: keep last portion
                overlap_text = chunk_text_joined[-chunk_overlap:] if chunk_overlap > 0 else ""
                current_chunk = [overlap_text] if overlap_text else []
                current_length = len(overlap_text)

            current_chunk.append(para)
            current_length += para_len

        if current_chunk:
            chunk_text_joined = "\n".join(current_chunk)
            if chunk_text_joined.strip():
                chunks.append({
                    "text": chunk_text_joined,
                    "chunk_index": chunk_index,
                    "heading": heading,
                    "char_count": len(chunk_text_joined),
                })
                chunk_index += 1

    return chunks


def _split_by_headings(text: str) -> list[dict[str, str]]:
    """Split text by markdown headings."""
    heading_pattern = re.compile(r"^(#{1,4})\s+(.+)$", re.MULTILINE)
    sections: list[dict[str, str]] = []
    last_end = 0
    last_heading = ""

    for match in heading_pattern.finditer(text):
        if match.start() > last_end:
            body = text[last_end:match.start()].strip()
            if body or last_heading:
                sections.append({"heading": last_heading, "body": body})

        last_heading = match.group(2).strip()
        last_end = match.end()

    # Remaining text
    remaining = text[last_end:].strip()
    if remaining or last_heading:
        sections.append({"heading": last_heading, "body": remaining})

    if not sections:
        sections.append({"heading": "", "body": text})

    return sections


def _split_by_paragraphs(text: str) -> list[str]:
    """Split text by paragraph boundaries."""
    paragraphs = re.split(r"\n\s*\n", text)
    result: list[str] = []

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If paragraph is too long, split by sentences
        if len(para) > DEFAULT_CHUNK_SIZE:
            sentences = _split_by_sentences(para)
            result.extend(sentences)
        else:
            result.append(para)

    return result


def _split_by_sentences(text: str) -> list[str]:
    """Split text by Japanese sentence boundaries."""
    # Japanese sentence endings: 。！？ and newlines
    sentences = re.split(r"(?<=[。！？\n])\s*", text)
    return [s.strip() for s in sentences if s.strip()]
