from ..document import NLUDocList, NLUDoc
from .base import BaseDocStore
from docarray import DocList


class NLUDocStore(BaseDocStore):
    bucket_name = 'nlu'
    
    @classmethod
    def pull(cls, name: str, show_progress: bool = True) -> NLUDocList:
        name = name.strip()
        docs = DocList[NLUDoc].pull(url=f's3://{cls.bucket_name}/{name}', show_progress=show_progress)
        return NLUDocList(docs)
    
    @classmethod
    def push(cls, docs: NLUDocList, name: str, show_progress: bool = True) -> None:
        name = name.strip()
        _ = DocList[NLUDoc].push(docs, url=f's3://{cls.bucket_name}/{name}', show_progress=show_progress)
        return