def split_text(
        text: str,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("Chunk Size must be greater than 0")

    if chunk_overlap < 0:
        raise ValueError("Chunk Overlap cannot be negative")

    if chunk_overlap >= chunk_size:
        raise ValueError("Chunk Overlap must be smaller than Chunk Size")

    text = " ".join(text.split())

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end]
        chunks.append(chunk)

        if end >= len(text):
            break

        start = end - chunk_overlap

    return chunks