from docarray import BaseDoc, DocList
from docarray.typing import NdArrayEmbedding
from docarray.utils.filter import filter_docs
import numpy as np
from tqdm import tqdm
import json
from typing import List
from wasabi import msg


class EmbeddingDoc(BaseDoc):
    """存放词(字)向量的文档
    """
    text: str
    embedding: NdArrayEmbedding
    
    def __hash__(self) -> int:
        return hash(self.text)
    
    def __eq__(self, other) -> bool:
        return self.text == other.text
    
    
class EmbeddingDocList(DocList[EmbeddingDoc]):
    
    @classmethod
    def from_file(cls, file_path: str):
        """从文件中读取词向量
        """
        docs = EmbeddingDocList()
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in tqdm(lines):
                token = line.strip().split(' ')[0]
                embeddings = line.strip().split(' ')[1:]
                embeddings = [float(i) for i in embeddings]
                doc = EmbeddingDoc(text=token, embedding=embeddings)
                docs.append(doc)
        return docs
    
    
    def get_vocab(self):
        """获取词表
        """
        return {doc.text: i for i, doc in enumerate(self)}
    
    def get_embeddings(self):
        """获取所有向量多用于构建embedding层
        """
        embeddings = [doc.embedding for doc in self]
        return np.array(embeddings, dtype=np.float32)
    
    def save_vocab_json(self, file_path: str):
        """保存词表json文件
        """
        vocab = self.get_vocab()
        with open(file_path, 'w') as f:
            json.dump(vocab, f)
            
    def save_vocab_txt(self, file_path: str):
        """保存词表txt文件
        """
        vocab = self.get_vocab()
        with open(file_path, 'w') as f:
            for k, v in vocab.items():
                f.write(f'{k} {v}\n')
                
    def extend_from_embeddings(self, tokens: List[str], embeddings: "EmbeddingDocList") -> "EmbeddingDocList":
        """从另一个EmbeddingDocList中扩展词向量
        """
        for token in tokens:
            query = {"text": {"$eq": token}}
            results = filter_docs(embeddings, query)
            if len(results) > 0:
                src_docs = filter_docs(self, query)
                if len(src_docs) == 0:
                    self.append(results[0])
                    msg.good(f'extend token {token} success')
                else:
                    msg.fail(f'token {token} already exists')
                    