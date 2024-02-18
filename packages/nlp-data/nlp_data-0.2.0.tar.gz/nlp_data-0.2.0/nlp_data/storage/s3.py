import boto3
from wasabi import msg
from rich.table import Table
from rich.console import Console
from typing import List, Optional
from pathlib import Path



class S3Storage():
    def __init__(self, 
                 endpoint_url: str = "http://192.168.130.5:9005", 
                 access_key: str = "minioadmin", 
                 secret_key: str = "minioadmin"):
        super().__init__()
        self.s3 = boto3.resource(service_name='s3',
                                 endpoint_url=endpoint_url,
                                 aws_access_key_id=access_key,
                                 aws_secret_access_key=secret_key)
        self.s3_client = boto3.client('s3')
        
    @property
    def buckets(self):
        return [b.name for b in self.s3.buckets.all()]
    
    def check_bucket(self, bucket_name: str) -> bool:
        """检查bucket是否存在
        """
        if bucket_name not in self.buckets:
            return False
        return True
    
    def _get_bucket_files(self, bucket_name: str) -> List[str]:
        """获取某个bucket下的所有文件名称
        """
        return [obj.key for obj in self.s3.Bucket(bucket_name).objects.all()]
     
    def list_buckets(self, show_table: bool = True) -> List[str]:
        """基于rich库更好的展示所有的bucket的名称和文件数量"""
        all_buckets = self.buckets
        if show_table:
            table = Table(title="Buckets", show_header=True, header_style="bold magenta")
            table.add_column("Bucket Name", style="dim", width=12)
            table.add_column("File Count", justify="right", width=12)
            for bucket in self.s3.buckets.all():
                table.add_row(bucket.name, str(len(list(bucket.objects.all()))))
            console = Console()
            console.print(table)
        return all_buckets
        
    def list_files(self, bucket_name: str, show_table: bool = True) -> List[str]:
        """基于rich库更好的展示某个bucket下的所有文件的名称"""
        if bucket_name not in self.buckets:
            msg.fail(f"Bucket {bucket_name} does not exist.")
            return
        all_files = self._get_bucket_files(bucket_name)
        if show_table:
            table = Table(title=f"Files in {bucket_name}", show_header=True, header_style="bold magenta")
            table.add_column("File Name", style="dim")
            table.add_column("Size", justify="right")
            table.add_column("Last Modified", justify="right")
            for obj in self.s3.Bucket(bucket_name).objects.all():
                size = obj.size / 1024 / 1024
                if 1 <= size < 1024:
                    size = f"{size:.2f} MB"
                elif size <1:
                    size = f"{size * 1024:.2f} KB"
                elif 1024 <= size < (1024 * 1024):
                    size = f"{size / 1024:.2f} GB"
                elif size >= 1024 * 1024:
                    size = f"{size / 1024 / 1024:.2f} TB"
                last_modified = obj.last_modified.strftime("%Y-%m-%d %H:%M:%S")
                table.add_row(obj.key, size, last_modified)
            console = Console()
            console.print(table)
        return all_files
        
    def create_bucket(self, bucket_name: str):
        """创建一个bucket
        """
        if bucket_name in self.buckets:
            msg.fail(f"Bucket {bucket_name} already exists.")
        else:
            self.s3.create_bucket(Bucket=bucket_name)
            msg.good(f"Bucket {bucket_name} created.")
            
    def delete_bucket(self, bucket_name: str):
        """删除一个bucket
        """
        if bucket_name not in self.buckets:
            msg.fail(f"Bucket {bucket_name} does not exist.")
        else:
            for obj in self.s3.Bucket(bucket_name).objects.all():
                obj.delete()
            self.s3.Bucket(bucket_name).delete()
            msg.good(f"Bucket {bucket_name} deleted.")
            
    def delete_file(self, bucket_name: str, file_name: str):
        """根据文件名删除文件
        """
        if bucket_name not in self.buckets:
            msg.fail(f'{bucket_name} not found')
            return
        all_files = self._get_bucket_files(bucket_name)
        if file_name not in all_files:
            msg.fail(f'{file_name} not found or is a directory')
            return
        self.s3.Bucket(bucket_name).Object(file_name).delete()
        msg.good(f'{file_name} deleted')
    
    def delete_dir(self, bucket_name: str, dir_name: str):
        """根据文件夹名称删除文件夹
        """
        if bucket_name not in self.buckets:
            msg.fail(f'{bucket_name} not found')
            return
        for obj in self.s3.Bucket(bucket_name).objects.all():
            if obj.key.split('/')[0] == dir_name:
                obj.delete()
                msg.good(f'{obj.key} deleted')
            
    def upload_file(self, file_path: str, bucket_name: str, object_name: Optional[str] = None):
        """上传文件
        """
        file_path: Path = Path(file_path)
        if file_path.is_file():
            if bucket_name not in self.buckets:
                msg.fail(f'{bucket_name} not found')
            if object_name is None:
                object_name = file_path.name
            self.s3_client.upload_file(file_path, bucket_name, object_name)
            msg.good(f'{object_name} uploaded')
        else:
            msg.fail(f'{file_path} is not a file. if you want to upload a directory, use upload_dir')
            return
        
        
    def download_file(self, 
                      bucket_name: str, 
                      object_name: str, 
                      save_path: Optional[str] = None):
        """下载文件
        """
        if bucket_name not in self.buckets:
            msg.fail(f'{bucket_name} not found')
            return
        object_name = object_name.strip()
        all_files = self._get_bucket_files(bucket_name)
        if object_name not in all_files:
            msg.fail(f'{object_name} not found')
            return
        if not save_path:
            save_path: Path = Path('./', object_name)
        else:
            save_path: Path = Path(save_path)
        if not save_path.parent.exists():
            save_path.parent.mkdir(parents=True)
        self.s3_client.download_file(Bucket=bucket_name, Key=object_name, Filename=save_path)
        msg.good(f'{object_name} downloaded to {save_path}')
    
    
    def upload_dir(self, bucket_name: str, dir: str):
        """上传文件夹, 会递归上传文件夹下的所有文件,文件会以如下方式保存:
        dir/file1.txt -> bucket_name/dir/file1.txt
        dir/dir2/file2.txt -> bucket_name/dir/dir2/file2.txt
        
        args:
            dir: 本地文件夹路径
            bucket_name: 上传到的bucket名称
            object_name: 上传到bucket下的文件夹名称, 默认为本地文件夹名称
        """
        dir: Path = Path(dir) 
        if dir.is_file():
            msg.fail(f'{dir} is not a directory')
            return
        if bucket_name not in self.buckets:
            msg.fail(f'{bucket_name} not found')
            return
        all_objects = self._get_bucket_files(bucket_name)
        def _upload_file(file_path: Path, pre_path: str):
            if file_path.is_file():
                self.upload_file(file_path, bucket_name, (pre_path + '/' + file_path.name).strip('/'))
            elif file_path.is_dir():
                for path in file_path.iterdir():
                    _upload_file(path, (pre_path + '/' + file_path.name).strip('/'))
        _upload_file(dir, '')
        
    
    def download_dir(self, bucket_name: str, object_name: str, save_dir: Optional[str] = None):
        """下载文件夹, 会递归下载文件夹下的所有文件,文件会以如下方式保存:
        bucket_name/dir/file1.txt -> save_dir/dir/file1.txt
        bucket_name/dir/dir2/file2.txt -> save_dir/dir/dir2/file2.txt
        
        args:
            bucket_name: 下载的bucket名称
            object_name: 下载的bucket下的文件夹名称
            save_dir: 下载到本地的文件夹路径
        """
        if not save_dir:
            save_dir: Path = Path('./')
        else:
            save_dir: Path = Path(save_dir)
        if bucket_name not in self.buckets:
            msg.fail(f'{bucket_name} not found')
            return
        
        object_name = object_name.strip()
        all_files = self._get_bucket_files(bucket_name)
        # 确保是个文件夹
        all_objects = [obj for obj in all_files if obj.split('/')[0] == object_name and len(obj.split('/')) > 1]
        if len(all_objects) == 0:
            msg.fail(f'{object_name} not found')
            return
        if not save_dir.is_dir():
            save_dir.mkdir(parents=True)
        for obj in all_objects:
            save_path = Path(save_dir, obj)
            self.download_file(bucket_name, obj, save_path=save_path)
            
            
    def rename(self, bucket_name: str, object_name: str, new_name: str):
        """重命名文件
        """
        if bucket_name not in self.buckets:
            msg.fail(f'{bucket_name} not found')
            return
        object_name = object_name.strip()
        all_files = self._get_bucket_files(bucket_name)
        if object_name not in all_files:
            msg.fail(f'{object_name} not found')
            return
        self.s3_client.copy_object(Bucket=bucket_name, CopySource=f'{bucket_name}/{object_name}', Key=new_name)
        self.s3_client.delete_object(Bucket=bucket_name, Key=object_name)
        msg.good(f'{object_name} renamed to {new_name}')