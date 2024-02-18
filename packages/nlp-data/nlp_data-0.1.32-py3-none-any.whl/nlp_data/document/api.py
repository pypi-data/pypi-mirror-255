from docarray import BaseDoc, DocList
from docarray.typing import NdArray
from typing import List, Optional, Dict
from tqdm import tqdm
from wasabi import msg
from pydantic import constr
from lightning_utilities.core.imports import RequirementCache

pandas_installed = bool(RequirementCache('pandas'))
Description = constr(strip_whitespace=True, min_length=1)


class APIParam(BaseDoc):
    name: str
    type: str = None
    description: Description = None
    required: str = True

class APIDoc(BaseDoc):
    name: str
    description: Description = None
    params: DocList[APIParam] = DocList[APIParam]()
    embedding: NdArray[768] = None
    score: Optional[float] = None
    extra: Optional[Dict] = None
    
    
class APIDocList(DocList[APIDoc]):
    
    
    def quick_add(self, api_name: str, param_names: List[str] = []):
        """快速添加API文档

        Args:
            api_name (str): 名称
            param_names (List[str]): 参数名称列表

        Returns:
           : APIDocList
        """
        params = [APIParam(name=param_name) for param_name in param_names]
        self.append(APIDoc(name=api_name, params=params))
        return self
    
    @classmethod
    def from_excel(cls, 
                   path: str,
                   api_name_col: str = '意图描述', 
                   api_description_col: str = '动作描述', 
                   param_name_col: str = '参数名称',
                   param_type_col: str = '参数类型',
                   param_description_col: str = '参数描述',
                   param_required_col: str = '参数是否必须') -> "APIDocList[APIDoc]":
        """从excel中读取API文档,格式如下:
        | 意图描述 | 动作描述 | 参数名称 | 参数类型 | 参数描述 | 参数是否必须 |

        Args:
            path (str): excel路径
            api_name_col (str, optional): API名字的列. Defaults to '意图描述'.
            api_description_col (str, optional): 描述API的列. Defaults to '动作描述'.
            param_name_col (str, optional): 参数名字列. Defaults to '参数名称'.
            param_type_col (str, optional): 参数类型列. Defaults to '参数类型'.
            param_description_col (str, optional): 参数描述列. Defaults to '参数描述'.
            param_required_col (str, optional): 参数必须列. Defaults to '参数是否必须'.

        Returns:
            APIDocList: API文档列表
        """
        if not pandas_installed:
            raise ImportError('pandas未安装, 你可以通过pip install nlp[all] 安装所有依赖')
        else:
            import pandas as pd
        dfs = pd.read_excel(path, sheet_name=None, usecols=[api_name_col, api_description_col, param_name_col, param_type_col, param_description_col, param_required_col])
        docs = APIDocList()
        for key in tqdm(dfs):
            df = dfs[key]
            for index, row in df.iterrows():
                current_api_name = row[api_name_col]
                if current_api_name is not None and current_api_name != '' and str(current_api_name) != 'nan':
                    docs.append(APIDoc(name=row[api_name_col], description=row[api_description_col]))
                    if row[param_name_col] is not None and row[param_name_col] != '' and str(row[param_name_col]) != 'nan':
                        docs[-1].params.append(APIParam(name=row[param_name_col], type=row[param_type_col], description=row[param_description_col], required=row[param_required_col]))
                else:
                    if row[param_name_col] is not None and row[param_name_col] != '' and str(row[param_name_col]) != 'nan':
                        docs[-1].params.append(APIParam(name=row[param_name_col], type=row[param_type_col], description=row[param_description_col], required=row[param_required_col]))
            msg.good(f'成功读取{key}的API文档')
        return docs