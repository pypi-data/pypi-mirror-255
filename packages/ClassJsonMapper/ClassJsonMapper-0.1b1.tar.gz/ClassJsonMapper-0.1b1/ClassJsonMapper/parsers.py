import re
from typing import Union
from .Errors import ListIndexError, DictKeyError


def SubscriptParser(sub: str) -> list:
    """
    对下标解析

    :params
        sub [str]: 需要解析的字符串下标
    :return list
    """
    result = [0, None]

    splitKey = re.search(r"\[(.*):(.*)\]", sub, re.S)
    if splitKey is None:
        return result

    if len(splitKey.group(1).strip()) != 0:
        result[0] = eval(splitKey.group(1))
    if len(splitKey.group(2).strip()) != 0:
        result[-1] = eval(splitKey.group(2))

    return result


def KeysParser(
        source: dict,
        keys: str,
        file_path: str,
        write_data: Union[None, int, str, dict, list, bool] = None
    ) -> Union[str, int, dict, list]:
    """
    通过 keys 对 json 文件中的数据进行解析，处理。
    
    :params
        source [dict]: 原数据
        keys [str]: 需要解析的keys值
        file_path [str]: 文件路径
        write_data type=[None, int, str, ...] default=None: 需要写入的数据 
    
    :return Union[str, int, dict, list]
    """
    # 将源数据存储，并通过cache缓存下标指向的数据
    result = source
    cache = None

    # 给keys补全。
    if keys.startswith(".", 0) is False:
        keys = "." + keys
        keys = keys.split(".")[1:]

    # 将 key 值储存，用于后面需要更改的数据
    previous_key = []
    for key in keys:
        result_t = type(result).__name__
        if result_t == "list":
            try:
                key = int(key)
            except ValueError:
                pass

        # 当数据不为list，将直接提取并赋值给result
        if type(cache).__name__ != 'list' and not cache:
            try:
                cache = result[key]
                previous_key.append(key)
                result = cache
            except KeyError:
                raise DictKeyError(
                        f"未从“{file_path}”中查找到（key）：{key}" \
                        f"\nNot found (key) in '{file_path}': {key}"
                    )
            continue
        
        # 下标范围解析
        try:
            if str(key).startswith("[", 0) is False:
                try:
                    cache = result[key]
                    previous_key.append(key)
                    result = cache
                    continue
                except TypeError:
                    raise ListIndexError(
                        f"列表下标错误，keys：{keys}" \
                        f" \nList index error, keys: {keys}"
                    )

            start, end = SubscriptParser(key)
            if end == None:
                cache = result[start:]
            elif start == None:
                cache = result[:end]
            else:
                cache = result[start:end]
                
        except IndexError:
            raise ListIndexError(
                f"列表下标错误，keys：{keys}" \
                f"\nList index error, keys: {keys}"
            )

        previous_key.append(key)
        result = cache
    
    # 更改数据内容
    if write_data:
        previous_key_len = len(previous_key)
        previous_key_0_t = type(source[previous_key[0]]).__name__

        # 数据类型为str，直接更改
        if previous_key_0_t == "str":
            source[previous_key[0]] = write_data
            return source
        
        # 数据类型为list或dict
        if previous_key_0_t in ["list", "dict"]:
            if previous_key_len == 2:
                source[previous_key[0]][previous_key[1]] = write_data
                return source
            
            previous_key_1_t = type(source[previous_key[0]][previous_key[1]]).__name__
            if previous_key_1_t == "list":
                # 此处使用递归，将源数据设置为当前位置，并将需要匹配的表达式，向后移一位。
                source[previous_key[0]][previous_key[1]] = KeysParser(
                    source=source[previous_key[0]][previous_key[1]],
                    keys=".".join([str(i) for i in previous_key[2:]]),
                    file_path=file_path,
                    write_data=write_data
                )
            return source

    return result
