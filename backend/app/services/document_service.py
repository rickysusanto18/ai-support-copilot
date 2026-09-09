from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.rag.chunker import split_text
from app.rag.embeddings import embedding_service

def create_document(
        db: Session,
        title: str,
        content: str,
        source: str | None = None,
) -> Document:
    document = Document(
        title=title,
        content=content,
        source=source,
    )

    db.add(document)
    db.flush()

    chunks = split_text(content)

    embeddings = embedding_service.embed_texts(chunks)

    for index, (chunk, embedding) in enumerate(
        zip(chunks, embeddings)
    ):
        document_chunk = DocumentChunk(
            document_id=document.id,
            chunk_index=index,
            content=chunk,
            embedding=embedding,
        )

        db.add(document_chunk)

    db.commit()
    db.refresh(document)

    return document