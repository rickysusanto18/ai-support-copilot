from sqlalchemy.orm import Session

from app.llm.ollama_client import ollama_client
from app.llm.prompt_builder import build_rag_prompt
from app.services.retrieval_service import search_documents

def generate_answer(
        db: Session,
        question: str,
        top_k: int = 5,
        min_similarity: float = 0.35,
) -> str:
    search_response = search_documents(
        db=db,
        query=question,
        top_k=top_k,
        min_similarity=min_similarity,
    )

    prompt = build_rag_prompt(
        question=question,
        results=search_response.results,
    )

    answer = ollama_client.generate(prompt)

    return answer