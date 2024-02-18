import os
import json
from pathlib import Path
from typing import Dict, List, Union, Optional

import httpx
from nonebot import logger


def load_json(json_file: Path) -> Dict:
    if not json_file.exists() or os.path.getsize(json_file) == 0:
        logger.warning(f"文件 {json_file} 为空或不存在。")
        return {}
    try:
        with json_file.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"文件 {json_file} 未找到。")
    except json.JSONDecodeError:
        logger.error(f"文件 {json_file} 解码错误。")
    raise FileNotFoundError


def save_json(json_file, data: Dict) -> None:
    if not json_file.exists():
        raise FileNotFoundError(f"文件 {json_file} 不存在。")
    try:
        with json_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except json.JSONDecodeError:
        logger.error(f"文件 {json_file} 解码错误。")


def list_jpg_files(directory: Union[str, Path]) -> List[str]:
    """
    列出指定目录下的所有jpg文件的文件名（不包括子目录）。

    参数:
        directory (str): 要搜索的目录。

    返回:
        List: 包含所有找到的jpg文件名的列表。
    """
    return [os.path.splitext(file)[0] for file in os.listdir(directory) if file.endswith(".jpg")]


def string_to_list(input_str: str) -> list:
    """
    将使用[,]分割的字符串转换为列表。
    :param input_str: 输入字符串
    :return: 列表
    """
    return [item.strip() for item in input_str.split(",") if item.strip()]


async def find_key_by_value(data: Dict, value: str) -> Optional[str]:
    """
    从 JSON 文件中查找给定值对应的键。

    参数:
        json_file (str): JSON 文件的路径。
        value (str): 要查找的值。

    返回:
        str: 找到的键，如果没有找到则返回 None。
    """
    return next((key for key, values in data.items() if value in values), None)


async def identify_empty_value_keys(data: Dict) -> List[str]:
    """
    从 Dict 中查找值为空的键。

    参数:
        data (Dict): 要查找的 Dict。

    返回:
        List[str]: 找到的键列表。
    """
    return [key for key, values in data.items() if not values]


async def list_all_keys(data: Dict) -> List[str]:
    """
    列出 JSON 文件中的所有键。

    参数:
        json_file (str): JSON 文件的路径。

    返回:
        List[str]: JSON 文件中的所有键。
    """
    return list(data.keys())


async def merge_dicts(raw_data: Dict, update_data: Dict) -> Dict:
    """
    合并两个字典，如果键不存在，则添加键值对。
    :param raw_data: 原始字典
    :param update_data: 更新字典
    :return: 合并后的字典
    """
    for key, value in update_data.items():
        raw_data[key] = value
    return raw_data


async def check_url(url: str, proxy_url: Optional[str]) -> bool:
    try:
        proxies = {"all://": proxy_url} if proxy_url else None
        with httpx.Client(proxies=proxies, timeout=5) as client:
            response = client.head(url)
            return response.status_code == 200
    except (httpx.RequestError, httpx.TimeoutException):
        logger.error(f"检查URL {url} 时出错。")
        return False
