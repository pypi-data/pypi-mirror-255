import os
import json
from typing import Union

from .Errors import *
from .parsers import *


class Mapper:
    def __init__(
            self,
            file_path: str,
            mode: str = "r+",
            encoding: str = "utf-8",
            is_create: bool = True
        ) -> None:
        """
        Mapper / 映射入口

        :params
            file_path [type=str]: json文件路径
            mode [type=str, default="r+"]: 打开文件的模式
            encodeing [type=str, default="utf-8"]: 编码格式
            is_create [type=bool, default=True]: 判断目录是否存在，反之创建一个
        :return None
        """
        self.file_path = file_path
        self.mode = mode
        self.encoding = encoding

        if (os.path.isfile(file_path) is False) and is_create:
            self.mode = "w+"
        self.fp = open(
            file=file_path,
            mode=mode,
            encoding=encoding
        )

        self.file_data = None
        self.read()
    
    def read(self) -> dict:
        """
        读取文件
        :return dict
        """
        self.fp.seek(0)
        __read = self.fp.read()
        self.file_data = __read

        if self.fp is None:
            return {}
        if __read is not None:
            return json.loads(__read)
        
        return {}
    
    def get(
            self,
            keys: Union[str, None] = None
        ) -> Union[str, int, list, None]:
        """
        通过 keys 值获取相应数据

        :params
            key: Union[str, None] = None
        :return Union[str, int, list]
        """
        result = self.read()

        if keys is None:
            return result

        result = KeysParser(
            source=result,
            keys=keys,
            file_path=self.file_path
        )

        return result
    
    def set(
            self,
            keys: str,
            data: Union[str, int, list]
        ) -> Union[dict, None]:
        """
        通过keys表达式设置数据内容
        
        :params
            keys [str]: 表达式
            data Union[str, int, list]: 需要设置的数据

        :return Union[dict, None]
        """
        file_data: dict = json.loads(self.file_data)
        if file_data is None:
            return None
        
        if keys in file_data.keys():
            file_data[keys] = data
        else:
            file_data = KeysParser(
                source=file_data,
                keys=keys,
                file_path=self.file_path,
                write_data=data
            )

        self.file_data = json.dumps(file_data, indent=4)

        return file_data
    
    def write(self) -> bool:
        """
        将文件更改为w+模式，将当前存放在内存的数据写入到json文件中。

        :return bool
        """
        if self.file_data is None:
            return False
        
        # 将fp指针更改为w+模式"
        self.close()
        self.fp = open(
            self.file_path,
            mode="w+",
            encoding=self.encoding
        )
        self.fp.write(self.file_data)
        self.file_data = self.fp.read()
        return True
    
    def close(self) -> None:
        """
        关闭文件
        :return None
        """
        if self.fp:
            self.fp.close()
    
    def __enter__(self) -> object:
        return self

    def __exit__(
            self, 
            exc_type: Exception, 
            exc_val, exc_tb
        ) -> bool:
        self.close()

        # if exc_type:
        #     pass
        return False
        