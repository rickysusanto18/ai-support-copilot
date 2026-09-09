from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk

def search_similar_chunks(
        db: Session,
        query_embedding: list[float],
        top_k: int = 5,
        min_similarity: float = 0.35,
) -> list[tuple[DocumentChunk, float]]:
    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    )

    similarity = 1.0 - distance

    statement = (
        select(DocumentChunk, distance)
        .where(
            DocumentChunk.embedding.is_not(None),
            similarity >= min_similarity,
        )
        .order_by(distance)
        .limit(top_k)
    )

    results = db.execute(statement).all()

    return [
        (chunk, float(distance_value))
        for chunk, distance_value in results
    ]