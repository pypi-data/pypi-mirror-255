from ..document import EmbeddingDoc, EmbeddingDocList
from .base import BaseDocStore
from docarray import DocList

class EmbeddingDocStore(BaseDocStore):
    
    bucket_name = 'embedding'
    
    @classmethod
    def pull(cls, name: str, show_progress: bool = True) -> DocList[EmbeddingDoc]:
        name = name.strip()
        docs = DocList[EmbeddingDoc].pull(url=f's3://{cls.bucket_name}/{name}', show_progress=show_progress)
        return EmbeddingDocList(docs)
    
    @classmethod
    def push(cls, docs: DocList[EmbeddingDoc], name: str, show_progress: bool = True) -> None:
        name = name.strip()
        _ = DocList[EmbeddingDoc].push(docs, url=f's3://{cls.bucket_name}/{name}', show_progress=show_progress)
        return None