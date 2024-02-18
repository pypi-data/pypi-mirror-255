from docarray import BaseDoc, DocList
from docarray.typing import ID
from typing import List, Dict, Any, Optional, Union, Literal
from pathlib import Path
from pydantic import validator, constr, conint, validate_arguments, confloat
from tqdm import tqdm
from copy import deepcopy
from docarray.utils.filter import filter_docs
from random import randint, choices
from tqdm import tqdm
from lightning_utilities.core.imports import RequirementCache

datsets_requirement = bool(RequirementCache('datasets'))
pandas_requirement = bool(RequirementCache('pandas'))

Label = constr(strip_whitespace=True, min_length=1)
Index = conint(ge=0, strict=True)
Score = confloat(ge=0, le=1, strict=True)


def assert_span_text_in_doc(doc_text: str, span_text: str, span_indices: List[Index]) -> None:
    """检查span的文本与标注的下标对应doc文本一致

    Args:
        doc_text (str): doc文本
        span_text (str): span文本
        span_indices (List[Index]): 在文档中的下标
    """
    try:
        text = ''.join([doc_text[i] for i in span_indices])
    except Exception as e:
        print(span_indices)
        print(len(span_indices))
        raise e
    # 如果实体文本存在则确保实体文本与下标对应文本一致,确保标注正确
    assert text == span_text, f'文本: <{span_text}> 与下标文本: <{text}> 不一致'

class Intention(BaseDoc):
    id: ID = None
    text: Label
    score: Optional[Score] = None
    
class Domain(BaseDoc):
    id: ID = None
    text: Label
    score: Optional[Score] = None


class Entity(BaseDoc):
    id: ID = None
    text: constr(strip_whitespace=True, min_length=1)
    indices: List[Index]
    label: Label
    score: Optional[Score] = None
    
    def is_contiguous(self):
        """判断实体是否连续

        Returns:
            bool: 是否连续
        """
        return self.indices == list(range(self.indices[0], self.indices[-1] + 1))
    
    @validator('text')
    def validate_text(cls, v: str, values: dict):
        if v is not None:
            values['ori_text'] = v # 记录原始文本,以此修改下边列表
            return v.strip() # 左右没有空格并且有效字符不为0则返回原文
        else:
            return v
    
    @validator('indices')
    def validate_indices(cls, v: List[Index], values):
        v = sorted(v)
        if 'text' in values:
            if values['text']:
                assert len(values['ori_text']) == len(v), f'下标: <{v}>与原始文本: <{values["ori_text"]}>长度不符'
                start = values['ori_text'].index(values['text'])
                indices = v[start: start+len(values['text'])]
                del values['ori_text']
                return indices
            else:
                return v
        else:
            return v
        

class NLUDoc(BaseDoc):
    text: str
    language: Optional[Literal['zh', 'en']] = None
    domain: Optional[Domain] = None
    intention: Optional[Intention] = None
    slots: DocList[Entity] = DocList[Entity]()
    abnf_output: str = None
    
    @validate_arguments
    def set_slot(self, text: constr(strip_whitespace=True, min_length=1, strict=True), label: Label, indices: Optional[List[Index]] = None, score: Optional[Score] = None):
        if not indices:
            start = self.text.index(text)
            end = start + len(text)
            indices = list(range(start, end))
        slot = Entity(text=text, indices=indices, label=label, score=score)
        if slot not in self.slots:
            assert_span_text_in_doc(doc_text=self.text, span_text=text, span_indices=indices)
            self.slots.append(slot)
    
    @validate_arguments
    def set_domain(self, text: constr(strip_whitespace=True, min_length=1), score: Optional[Score] = None):
        self.domain = Domain(text=text, score=score)
    
    @validate_arguments
    def set_intention(self, text: constr(strip_whitespace=True, min_length=1), score: Optional[Score] = None):
        self.intention = Intention(text=text, score=score)
    
    @classmethod
    def from_abnf_output_line(cls, 
                              line: constr(strip_whitespace=True, min_length=1), 
                              domain: Label, 
                              intention: Label,
                              lang: Literal['zh', 'en'] = 'zh') -> "NLUDoc":
        """根据abnf数据的一行数据初始化NLUDoc

        Args:
            domain (Label): 领域
            intention (Label): 意图
            line (constr, optional): . Defaults to True, min_length=1).

        Returns:
            NLUDoc: nlu文档.
        """
        # text = ''
        text = []
        spans = line.strip().split(' ')
        ents = []
        ent_spans = []
        for idx, span in enumerate(spans):
            if span.startswith('B-'):
                label = span[2:]
                for _span in spans[idx+1:]:
                    if _span.startswith('I-') and _span[2:] == label:
                        if ent_spans:
                            if lang == 'zh':
                                ent = ''.join(ent_spans)
                            if lang == 'en':
                                ent = ' '.join(ent_spans)
                            ents.append((label, ent))
                    if not _span.startswith('I-') and not _span.startswith('B-'):
                        ent_spans.append(_span)
            if not span.startswith('I-') and not span.startswith('B-'):
                text.append(span)
        if lang == 'zh':
            text = ''.join(text)
        if lang == 'en':
            text = ' '.join(text)
        doc = NLUDoc(text=text, domain=Domain(text=domain), intention=Intention(text=intention))
        for ent in ents:
            label = ent[0]
            ent_text = ent[1]
            doc.set_slot(text=ent_text, label=label)
        doc.abnf_output = line.strip()
        return doc
    
    def __hash__(self) -> int:
        return hash(self.text)
    
    def __eq__(self, __value: object) -> bool:
        return self.text == __value.text
        
        
class NLUExample(BaseDoc):
    """存放NLU文档对, 主要用于存放NLU文档对的评估结果
    """
    id: ID = None
    x: NLUDoc
    y: NLUDoc
    
    @validator('x')
    def validate_x(cls, value: NLUDoc, values: dict):
        """确保x与y的文本一致
        """
        y = values.get('y', None)
        if y:
            assert value.text == y.text, f'x文本: <{value.text}>与y文本: <{y.text}>不一致'
        return value
    
    @validator('y')
    def validate_y(cls, value: NLUDoc, values: dict):
        """确保x与y的文本一致
        """
        x = values.get('x', None)
        if x:
            assert value.text == x.text, f'y文本: <{value.text}>与x文本: <{x.text}>不一致'
        return value
    
    @property
    def is_intention_badcase(self):
        """判断x与y的意图是否不一致
        """
        if not self.y.intention:
            return False
        elif not self.x.intention:
            return True
        else:
            return self.x.intention.text != self.y.intention.text
    
    @property   
    def is_domain_badcase(self):
        """判断x与y的领域是否不一致
        """
        if not self.y.domain:
            return False
        elif not self.x.domain:
            return True
        else:
            return self.x.domain.text != self.y.domain.text
    
    @property 
    def is_slot_badcase(self):
        """判断x与y的槽位是否不一致
        """
        # 数量不等
        if len(self.y.slots) != len(self.x.slots):
            return True
        # slot的文本或者label不一致
        y_texts = [slot.text for slot in self.y.slots]
        x_texts = [slot.text for slot in self.x.slots]
        if sorted(y_texts) != sorted(x_texts):
            return True
        x_labels = [slot.label for slot in self.x.slots]
        y_labels = [slot.label for slot in self.y.slots]
        if sorted(x_labels) != sorted(y_labels):
            return True
        return False
    
    @property
    def is_badcase(self):
        """判断x与y是否不一致
        """
        return self.is_intention_badcase or self.is_domain_badcase or self.is_slot_badcase
    
        
        
class NLUDocList(DocList[NLUDoc]):
    
    @classmethod
    def from_file(cls, file_path: Union[str, Path], domain: str) -> 'NLUDocList':
        """从文件中一行一行读取文本,并转换为NLUDocList

        Args:
            file_path (Union[str, Path]): 文件路径.
            
            domain (str): 领域名称.

        Returns:
            NLUDocList: NLU文档列表
        """
        file_path = Path(file_path)
        assert file_path.is_file(), f'文件: <{file_path}>不存在'
        docs = NLUDocList()
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in tqdm(lines):
                doc = NLUDoc(text=line)
                doc.set_domain(text=domain)
                docs.append(doc)
        return docs
        
    
    @classmethod
    def from_abnf_output(cls, 
                         abnf_output_dir: str, 
                         domain: str,
                         add_space: bool = False) -> 'NLUDocList':
        """将abnf输出转换为NLU文档,并存放在NLUDocList中

        Args:
            abnf_output_dir (str): abnf输出目录
            domain (str): 领域名称

        Returns:
            NLUDocList: NLU文档列表

        """
        return convert_abnf_to_nlu_docs(output_dir=abnf_output_dir, domain=domain, add_space=add_space)
    
    
    def convert_intention_to_text_classification_dataset(self, 
                                                         save_path: Optional[str] = None,
                                                         train_ratio: float = 0.8,   
                                                         split_test: Optional[bool] = False,
                                                         add_labels: Optional[bool] = True):
        """将NLUDocList转换为文本分类数据集

        Args:
            train_ratio (float, optional): 训练集划分比率. Defaults to 0.8.
            save_path (Optional[str], optional): 数据集保存路径. Defaults to None.
            split_test (Optional[bool], optional): 是否划分测试集. Defaults to False.
            add_labels (Optional[bool], optional): 是否添加多标签列表. Defaults to True.

        Returns:
            Optional[DatasetDict]: 转换后的数据集, 如果save_path为None则返回划分后的数据集.
        """
        if not datsets_requirement:
            raise ImportError('datasets not installed, please install datasets first, pip install datasets')
        else:
            from datasets import Dataset, DatasetDict
        if not pandas_requirement:
            raise ImportError('pandas not installed, please install pandas first, pip install pandas')
        else:
            import pandas as pd
        data = {'text': self.text, 'label': self.traverse_flat('intention__text')}
        df = pd.DataFrame(data)
        train_df = df.groupby('label').sample(frac=train_ratio)
        if not split_test:
            val_df = df.drop(train_df.index)
            ds = DatasetDict({'train': Dataset.from_pandas(train_df, preserve_index=False), 'validation': Dataset.from_pandas(val_df, preserve_index=False)})
        else:
            val_ratio = (1 - train_ratio) / 2
            val_df = df.drop(train_df.index).groupby('label').sample(frac=val_ratio)
            test_df = df.drop(train_df.index).drop(val_df.index)
            ds = DatasetDict({'train': Dataset.from_pandas(train_df, preserve_index=False), 'validation': Dataset.from_pandas(val_df, preserve_index=False), 'test': Dataset.from_pandas(test_df, preserve_index=False)})
        if add_labels:
            ds = ds.map(lambda example: {'labels': [example['label']]})
        if save_path:
            ds.save_to_disk(save_path)
        else:
            return ds
        
    
    
    def convert_slots_to_ner_dataset(self, 
                                     save_path: Optional[str] = None,
                                     train_ratio: float = 0.8,  
                                     split_test: Optional[bool] = False):
        """将NLUDocList转换为NER数据集

        Args:
            train_ratio (float, optional): 训练集划分比率. Defaults to 0.8.
            save_path (Optional[str], optional): 数据集保存路径. Defaults to None.
            split_test (Optional[bool], optional): 是否划分测试集. Defaults to False.

        Returns:
            Optional[DatasetDict]: 转换后的数据集, 如果save_path为None则返回划分后的数据集.
        """
        if not datsets_requirement:
            raise ImportError('datasets not installed, please install datasets first, pip install datasets')
        else:
            from datasets import Dataset, DatasetDict
        if not pandas_requirement:
            raise ImportError('pandas not installed, please install pandas first, pip install pandas')
        else:
            import pandas as pd
        data = {'text': self.text, 'ents': [[ent.dict(exclude={"id"}) for ent in ent_ls] for ent_ls in self.slots]}
        df = pd.DataFrame(data)
        train_df = df.sample(frac=train_ratio)
        if not split_test:
            val_df = df.drop(train_df.index)
            ds = DatasetDict({'train': Dataset.from_pandas(train_df, preserve_index=False), 'validation': Dataset.from_pandas(val_df, preserve_index=False)})
        else:
            val_ratio = (1 - train_ratio) / 2
            val_df = df.drop(train_df.index).sample(frac=val_ratio)
            test_df = df.drop(train_df.index).drop(val_df.index)
            ds = DatasetDict({'train': Dataset.from_pandas(train_df, preserve_index=False), 'validation': Dataset.from_pandas(val_df, preserve_index=False), 'test': Dataset.from_pandas(test_df, preserve_index=False)})
        if save_path:
            ds.save_to_disk(save_path)
        else:
            return ds
        
    def convert_intention_to_fasttext_dataset(self, save_path: str = 'train.txt', split_type: Literal['char', 'no_split'] = 'char'):
        """转换为fasttext的数据格式txt文件,文本将按照字符进行切分

        Args:
            save_path (str): 保存目录
        """
        with open(save_path, 'w') as f:
            for doc in self:
                if doc.intention:
                    if split_type == 'char':
                        f.write(f"__label__{doc.intention.text} {' '.join(list(doc.text))}" + "\n")
                    else:
                        f.write(f"__label__{doc.intention.text} {doc.text}" + "\n")
        
    def convert_to_llm_nlu_dataset(self, valid_ratio: float = 0.2, save_path: Optional[str] = None):
        """将NLUDocList转换为LLM的NLU数据集,用于训练基于LLM做NLU结果生成的模型.
        
        - 模板示例: 你需要为用户的输入做如下的任务: 1.选择一种领域类型.以下是所有领域类型:{"domain1", "domain2", "domain3"}. 2.选择一种意图类型,以下是所有意图类型:{"intention1", "intention2", "intention3"} 3. 抽取所有实体以及其对应的标签,以下是所有实体类型:{"entity1", "entity2", "entity3"}
        """
        if not datsets_requirement:
            raise ImportError('datasets not installed, please install datasets first, pip install datasets')
        else:
            from datasets import Dataset
        entity = set([ent.label for doc in self for ent in doc.slots])
        domain = set([doc.domain.text for doc in self if doc.domain])
        intention = set([doc.intention.text for doc in self if doc.intention])
        
        ## 获得一个真实模板
        for example in self:
            if len(example.slots) > 0:
                example_input = example.text
                example_response = {"domain":f"{example.domain.text}","intention":f"{example.intention.text}", "entity":[]}
                for ent in example.slots:
                    example_response['entity'].append({'text':ent.text, 'label':ent.label})
        
        ## 构建指令
        base_instruction = f'你需要为用户的输入做如下的任务: 1.选择一种领域类型.以下是所有领域类型:{domain}. 2.选择一种意图类型,以下是所有意图类型:{intention} 3. 抽取所有实体以及对应类型, 以下是所有实体类型{entity}.并将结果以字典格式返回.例如:用户输入:{example_input}.输出:{example_response}'
        data = {"instruction": [], "input": [], "response": []}
        for i in range(len(self)):
            data['instruction'].append(base_instruction)
            data['input'].append(self[i].text)
            response = {"domain":"","intention":"", "entity":[]}
            if self[i].domain:
                response['domain'] = self[i].domain.text
            if self[i].intention:
                response['intention'] = self[i].intention.text
            if len(self[i].slots) > 0:
                for slot in self[i].slots:
                    response['entity'].append({'text':slot.text, 'label':slot.label})
            data['response'].append(response)
        ds = Dataset.from_dict(data)
        dsd = ds.train_test_split(test_size=valid_ratio)
        dsd['validation'] = dsd.pop('test')
        if save_path:
            dsd.save_to_disk(save_path)
        else:
            return dsd
        
    def compute_acc(self):
        """根据NLUExample的is_badcase方法计算准确率
        """
        assert self.doc_type == NLUExample, "该方法只能用于NLUExample类型的DocList"
        return 1 - sum(self.traverse_flat('is_badcase')) / len(self)
    
    
    def up_sampling_by_intention(self):
        """根据意图类型数据上采样, 使得每个意图类型的数量一致
        """
        intention_ls = self.traverse_flat('intention__text')
        intention_count = {intention: intention_ls.count(intention) for intention in set(intention_ls)}
        max_count = max(intention_count.values())
        for intention in tqdm(intention_count):
            query = {'intention__text': {'$eq': intention}}
            intention_docs = filter_docs(self, query)
            if len(intention_docs) < max_count:
                for _ in range(max_count - len(intention_docs)):
                    idx = randint(0, len(intention_docs) - 1)
                    self.append(deepcopy(intention_docs[idx]))
        return self
    
    def sample_by_intention(self, n_sample: int) -> 'NLUDocList':
        """根据意图类型采样, 使得每个意图类型的数量一致
        """
        docs = NLUDocList()
        intention_labels = set(self.traverse_flat('intention__text'))
        samples_per_intention = n_sample // len(intention_labels)
        for intention in intention_labels:
            query = {'intention__text': {'$eq': intention}}
            intention_docs = filter_docs(self, query)
            sample_docs = choices(intention_docs, k=samples_per_intention)
            docs.extend(sample_docs)
        return docs
    
    def check_language(self) -> str:
        """检查文档的语言是否一致
        """
        lang = set(self.traverse_flat('language'))
        assert len(lang) == 1, f'文档的语言不一致: {lang}'
        return lang.pop()

    def set_language(self, lang: Literal['zh', 'en']):
        """设置文档的语言
        """
        for doc in self:
            doc.language = lang
        
         

def convert_abnf_to_nlu_docs(output_dir: str, domain: str, error_pass: bool = True, add_space: bool = False) -> NLUDocList:
    """将abnf句式生成的数据转换NLUDoc并以DocList[NLUDoc]的形式返回
        
    注意:
    - 每个abnf输出文件的标题应该是对应的intention
    - 实体请以B-XXX, I-XXX的形式标注
    - 支持嵌套实体, 以B-XXX与之后遍历到的第一个I-XXX为实体

    参数:
    - output_dir (str): abnf输出文件夹
    - domain (str): 领域名称
    - error_pass (bool): 是否忽略错误, 默认为True
    - add_space (bool): 是否span之间添加空格, 主要用于英文, 默认为False.

    返回:
    - DocList: 转换后的NLUDocList
    """
    docs = NLUDocList()
    for f in Path(output_dir).iterdir():
        if f.is_file() and f.suffix == '.abnf_out':
            intention = f.stem
            with open(f, 'r') as f:
                lines = f.readlines()
                for line in tqdm(lines):
                    try:
                        if len(line.strip()) > 0:
                            text = ''
                            spans = line.strip().split(' ')
                            ents = []
                            for idx, span in enumerate(spans):
                                if span.startswith('B-'):
                                    label = span[2:]
                                    start = len(text)
                                    span_len = 0
                                    for _span in spans[idx+1:]:
                                        if _span.startswith('I-') and _span[2:] == label:
                                            end = start + span_len
                                            ents.append((label, start, end))
                                        if not _span.startswith('I-') and not _span.startswith('B-'):
                                            span_len += len(_span)
                                                
                                if not span.startswith('I-') and not span.startswith('B-'):
                                    text += span
                                    if add_space:
                                        text += ' '
                            doc = NLUDoc(text=text, domain=Domain(text=domain), intention=Intention(text=intention))
                            for ent in ents:
                                label = ent[0]
                                start = ent[1]
                                end = ent[2]
                                doc.set_slot(text=text[start:end], indices=list(range(start, end)), label=label)
                            doc.abnf_output = line.strip()
                            docs.append(doc)   
                    except Exception as e:
                        print(f'转换错误: {e}')
                        pass
    return docs