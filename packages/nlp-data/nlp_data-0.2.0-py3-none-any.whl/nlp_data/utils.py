from .storage import NLUDocStore
from .document import NLUDocList
from random import shuffle
from pathlib import Path
import psutil
from typing import Callable
from wasabi import msg
import time

def create_domain_fasttext_dataset(pos_domain_name: str, num_neg_docs: int = 20000, dataset_path: str = './dataset/domain.txt') -> None:
    """将NLUDocStore中的数据集转换为fasttext的数据集格式

    Args:
        pos_domain_name (str): 正例的领域名称, 例如: `schedule`,会匹配文件名称中包含`schedule`的文件
        num_neg_docs (int, optional): 每个负例领域文档的数量. Defaults to 20000.
        dataset_path (str, optional): 数据集的保存路径. Defaults to './dataset/domain.txt'.
    """
    dataset_path: Path = Path(dataset_path)
    if dataset_path.exists():
        dataset_path.unlink()
    else:
        dataset_path.parent.mkdir(parents=True, exist_ok=True)
    doc_names = NLUDocStore.list(show_table=False)
    pos_doc_names = [doc_name for doc_name in doc_names if pos_domain_name in doc_name]
    neg_doc_names = [doc_name for doc_name in doc_names if pos_domain_name not in doc_name]
    # 首先下载全部正例数据
    pos_docs: NLUDocList = NLUDocList()
    for doc_name in pos_doc_names:
        pos_docs.extend(NLUDocStore.pull(doc_name))
    with open(dataset_path, 'a') as f:
        for doc in pos_docs:
            text = ' '.join(list(doc.text))
            f.write(f'__label__1# {text}')
    # 然后下载全部负例数据
    neg_docs = NLUDocList()
    for doc_name in neg_doc_names:
        neg_doc = NLUDocStore.pull(doc_name)
        shuffle(neg_doc)
        neg_docs.extend(neg_doc[:num_neg_docs])
    # 保存数据集
    with open(dataset_path, 'a') as f:
        for doc in neg_docs:
            text = ' '.join(list(doc.text))
            f.write(f'__label__0# {text}')


def get_cpu_memory(tag: str):
    """获取函数运行时的cpu内存

    Args:
        tag (str): 标签
    """
    def out_wrapper(fn: Callable):
        def wrapper(*args, **kwargs):
            p = psutil.Process()
            cpu_memory = p.memory_info().rss
            outputs = fn(*args, **kwargs)
            cpu_memory = p.memory_info().rss - cpu_memory
            msg.good(f"{tag} cpu memory: {cpu_memory / 1024 / 1024}MB")
            return outputs
        return wrapper
    return out_wrapper

def get_spent_time(tag: str):
    """获取函数运行时的时间

    Args:
        tag (str): 标签
    """
    def out_wrapper(fn: Callable):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            outputs = fn(*args, **kwargs)
            end_time = time.time()
            msg.good(f"{tag} spent time: {end_time - start_time}")
            return outputs
        return wrapper
    return out_wrapper