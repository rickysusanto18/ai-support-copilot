from app.db.database import Base, engine
from app.models.document import Document
from app.models.document_chunk import DocumentChunk

def init_db() -> None:
    Base.metadata.create_all(bind=engine)