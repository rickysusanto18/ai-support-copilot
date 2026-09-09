from sqlalchemy.orm import session

from app.rag.embeddings import embedding_service
from app.repositories.document_repository import search_similar_chunks
from app.schemas.search import SearchResponse, SearchResult

def search_documents(
        db: session,
        query: str, 
        top_k: int,
        min_similarity: float,
) -> SearchResponse:
    query_embedding = embedding_service.embed_text(query)

    results = search_similar_chunks(
        db=db,
        query_embedding=query_embedding,
        top_k=top_k,
        min_similarity=min_similarity,
    )

    search_results = []

    for chunk, distance in results:
        similarity = 1.0 - distance

        search_results.append(
            SearchResult(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                similarity=similarity,
            )
        )

    return SearchResponse(
        query=query,
        results=search_results,
    )