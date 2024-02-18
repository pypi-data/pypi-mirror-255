## 普强内部NLP数据存储分享工具


### 安装

<details>
<summary>pypi安装</summary>

```bash
# 安装基本功能
pip install nlp-data
# 安装全部功能
pip install nlp-data[all]
```
</details>

<details>
<summary>普强源安装</summary>

```bash
pip install nlp-data --upgrade -i http://192.168.130.5:5002/simple/ --trusted-host 192.168.130.5 --extra-index-url https://mirrors.aliyun.com/pypi/simple
```

</details>

### 使用
<details>
<summary><b>Store的使用</b></summary>

```python 
    # Store相当于是S3对象存储的一个Bucket的封装,每个数据类型对应一个Bucket
    from nlp_data import NLUDocStore
    # 查看文档
    NLUDocStore.list()
    # 获取文档
    docs = NLUDocStore.pull('xxx')
    # 推送文档
    NLUDocStore.push(docs=docs, name='xxx')
```
</details>

<details>
<summary><b>Doc的使用</b></summary>

  ```python
      # Doc是nlp-data的一个存储结构,可以用来存储该格式的数据,以及对数据进行一些操作
      # DocList是Doc的集合,可以用来存储多个Doc,相当于一个python List,有几本的append,extend等类方法, 但不同的DocList有特定的方法用来处理# 该数据类型
      # 以NLUDoc为例,该文档里面有domain,slots,intention等字段,可以用来存储NLU的结果
      from nlp_data import NLUDoc, NLUDocList
      # 创建一个NLUDoc
      doc = NLUDoc(text='添加明天上午跟张三开会的提醒')
      doc.set_domain('schedule_cmn')
      doc.set_intention('add_schedule')
      doc.set_slot(text='明天上午', label='date')
      doc.set_slot(text='跟张三开会', label='title')
      # 创建一个NLUDocList,并添加doc
      docs = NLUDocList()
      docs.append(doc)
      # 从abnf句式输出文件中批量初始化
      docs = NLUDocList.from_abnf_output(output_dir='your/dir', domain='schedule_cmn')
      # 上传到bucket
      from nlp_data import NLUDocStore
      NLUDocStore.push(docs=docs, name='xxx')
  ```
</details>

<details>
<summary><b>Augmentor</b>的使用</summary>

  ```python
    # Augmentor是nlp-data的一个数据增强工具,可以用来对数据进行增强
    from nlp_data import GPTAugmentor, NLUDocStore, DialogueDocList, DialogueDoc
    # 创建一个Augmentor
    augmentor = GPTAugmentor(api_key='xxx')
    # 广东话或者四川话增强NLUDoc
    docs = NLUDocStore.pull('xxx')
    aug_docs = augmentor.augment_nlu_by_localism(docs, '广东话')
    # 根据主题和情景生成多轮对话
    dialogue_docs = augmentor.generate_dialogue_docs(theme='添加日程', situation='用户正在驾驶车辆与车机系统丰田进行语音交互')
    # 对多轮对话数据增强
    dialogue_docs = DialogueDocList()
    dialogue_docs.quick_add(theme='添加日程', situation='用户正在驾驶车辆与车机系统丰田进行交互', conversation=['你好,丰田', '在呢,有什么可以帮助你的', '我要添加一个明天上午跟张三开会的日程', '好的已为您添加成功'])
    aug_dialogue_docs = augmentor.augment_dialogue(dialogue_docs)
  ```
  </details>

<details>
<summary><b>S3的使用</b></summary>

  s3是基础的S3对象存储的封装,可以用来创建bucket,上传下载文件等
  ```python
    # 初始化
    s3 = S3Storage()
    # 列出所有bucket
    s3.list_buckets()
    # 创建bucket
    s3.create_bucket('test')
    # 列出bucket下所有文件
    s3.list_files('test')
    # 上传文件
    s3.upload_file(file_path='./test.txt', bucket_name='test')
    # 下载文件
    s3.download_file(object_name='./test.txt', bucket_name='test')
    # 删除文件
    s3.delete_file(bucket_name='test', file_name='test.txt')
    # 上传文件夹
    s3.upload_dir(bucket_name='test', dir='./tests')
    # 下载文件夹
    s3.download_dir(bucket_name='test', object_name='./tests', save_dir='./')
    # 删除文件夹
    s3.delete_dir(bucket_name='test', dir_name='tests')
    # 删除bucket
    s3.delete_bucket('test')
  ```
</details>

<details>
<summary><b>命令行</b></summary>

```bash
# 查看帮助
nlp-data --help
# 下载文件,当xxx为一个s3中的文件夹时,会下载该文件夹下所有文件
nlp-data download xxx.xxx --bucket xxx --save_path xxx
# 上传文件, 当xxx为一个文件夹时,会上传该文件夹下所有文件
nlp-data upload xxx --bucket xxx
# 删除文件, 当xxx为一个文件夹时,会删除该文件夹下所有文件
nlp-data delete xxx --bucket xxx
```
</details>

### 更新日志

<details>
<summary>0.1.7</summary>

- 增加了NLUDocList的from_file方法,可以从文件中批量初始化NLUDocList,需要文件为一行一个文本的格式
  ```python
  from nlp_data import NLUDocList

  docs = NLUDocList.from_file('your/file/path', domain='domain_name')
  ```
</details>

<details>
<summary>0.1.8</summary>

- 修复了docarray 0.39版本的无法导入的bug
- 新增命令行工具
  ```bash
  nlp-data --help
  ```
</details>

<details>
<summary>0.1.10</summary>

- 减少了基本依赖
- 完善了命令行工具
  ```bash
  nlp-data --help
  ```
</details>
<details>
<summary>0.1.12</summary>

- 修复: 
  - 修复了S3Storage里面由于缓存buckets带来的bug。
  - 默认不在依赖pandas
- 添加:
  - 命令行显示文件添加了最后修改时间。
  - 完善了README.md
</details>
<details>
<summary>0.1.13</summary>

- 修复: 
  - CLI的下载保存路径无法修改的BUG。
</details>
<details>
<summary>0.1.16</summary>

- 修改: 
  - 删除了无用依赖。
- 添加:
  - 增加了`NLUDoclist.convert_to_fasttext_dataset`用于方便讲nlu数据转化为fasttext格式数据,参数: save_path 保存路径
</details>
<details>
<summary>0.1.18</summary>

- 修改: 
  - 修改docarray依赖错误问题。
</details>

<details>
<summary>0.1.23</summary>

- 添加:
  - 增加了`NLUDoclist.sample_by_intention`用于根据意图进行采样,参数: n_sample 采样数量
</details>
