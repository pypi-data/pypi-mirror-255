from ..document import DialogueDoc, DialogueDocList
from .base import BaseDocStore
from docarray import DocList


class DialogueDocStore(BaseDocStore):
    
    bucket_name = 'dialogue'
    
    @classmethod
    def pull(cls, name: str, show_progress: bool = True) -> DocList[DialogueDoc]:
        name = name.strip()
        docs = DocList[DialogueDoc].pull(url=f's3://{cls.bucket_name}/{name}', show_progress=show_progress)
        return DialogueDocList(docs)
    
    @classmethod
    def push(cls, docs: DocList[DialogueDoc], name: str, show_progress: bool = True) -> None:
        name = name.strip()
        _ = DocList[DialogueDoc].push(docs, url=f's3://{cls.bucket_name}/{name}', show_progress=show_progress)
        return None