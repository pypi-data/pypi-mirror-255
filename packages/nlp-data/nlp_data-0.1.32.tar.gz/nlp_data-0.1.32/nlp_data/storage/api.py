from .base import BaseDocStore
from ..document import APIDoc, APIDocList
from docarray import DocList

class APIDocStore(BaseDocStore):
    
    bucket_name = 'api'
    
    @classmethod
    def pull(cls, name: str, show_progress: bool = True) -> DocList[APIDoc]:
        name = name.strip()
        docs = DocList[APIDoc].pull(url=f's3://{cls.bucket_name}/{name}', show_progress=show_progress)
        return APIDocList(docs)
    
    @classmethod
    def push(cls, docs: DocList[APIDoc], name: str, show_progress: bool = True) -> None:
        name = name.strip()
        _ = DocList[APIDoc].push(docs, url=f's3://{cls.bucket_name}/{name}', show_progress=show_progress)
        return None