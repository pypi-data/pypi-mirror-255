import os
import re
import subprocess
from pathlib import Path
from typing import Union

from tqdm import tqdm
from nonebot import logger

from nonebot_plugin_bh3_elysian_realm.config import plugin_config


async def git_pull(image_path: Path) -> bool:
    clone_command = ["git", "pull"]

    if not os.path.exists(image_path):
        logger.error(f"目录 {image_path} 不存在")
        return False

    os.chdir(image_path)

    try:
        with subprocess.Popen(clone_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            stdout, stderr = process.communicate()

            if "Already up to date." in stdout:
                logger.info("图片资源已是最新版本")
            else:
                logger.info("图片资源开始更新")
                with tqdm(desc="更新中") as pbar:
                    for line in stderr.splitlines():
                        if speed_match := re.search(r"\|\s*([\d.]+\s*[\w/]+/s)", line):
                            speed = speed_match[1]
                            pbar.set_postfix_str(f"下载速度: {speed}")
                        pbar.update()
                logger.info("图片资源更新完成")
            return True
    except subprocess.CalledProcessError:
        logger.error("图片资源更新异常")
        return False


async def git_clone(repository_url: str, image_path: Path) -> Union[bool, str]:
    clone_command = ["git", "clone", "--progress", "--depth=1", repository_url, image_path]

    try:
        if os.path.exists(image_path) and os.listdir(image_path):
            logger.error(f"目录 {plugin_config.image_path} 不为空")
            return False
        if os.path.exists(image_path / ".gitkeep"):
            os.remove(image_path / ".gitkeep")
        with subprocess.Popen(clone_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
            with tqdm(desc="克隆中") as pbar:
                if process.stderr is not None:
                    for line in process.stderr:
                        if speed_match := re.search(r"\|\s*([\d.]+\s*[\w/]+/s)", line):
                            speed = speed_match[1]
                            pbar.set_postfix_str(f"下载速度: {speed}")
                        pbar.update()
                        if "done." in line:
                            logger.info("乐土攻略获取完成")
                            return True

    except subprocess.CalledProcessError as e:
        error_info = e.stderr
        if "fatal: destination path" in error_info:
            logger.warning(f"{error_info}\n{plugin_config.image_path}目录下已存在数据文件")
        else:
            logger.error(f"克隆异常:\n{error_info}")

        return False


async def contrast_repository_url(repository_url: str, path: Path) -> bool:
    """
    异步地检查指定目录是否为指定的 Git 仓库。

    此函数通过在指定目录执行 Git 命令来获取 Git 仓库的远程 URL。
    然后，它会将这个 URL 与提供的 URL 进行比较。

    参数:
        repository_url (str): 要检查的 Git 仓库的 URL。
        path (Path): 要检查的目录路径。

    返回:
        bool: 如果指定目录是指定的 Git 仓库，则返回 True；否则返回 False。

    异常:
        subprocess.CalledProcessError: 如果在执行 Git 命令时出错，将捕获此异常并返回 False。

    注意:
        这个函数假设 'git' 命令在系统路径上可用。
        如果指定目录不是 Git 仓库，或者 'git' 命令无法执行，函数将返回 False。
    """
    original_cwd = Path.cwd()
    try:
        os.chdir(path)
        remote_url = (
            subprocess.check_output(["git", "config", "--get", "remote.origin.url"], stderr=subprocess.STDOUT)
            .strip()
            .decode("utf-8")
        )
        if remote_url == repository_url:
            logger.debug("指定仓库地址与目录下仓库地址匹配")
            return True
        else:
            logger.debug(f"目录下仓库地址: {remote_url}")
            logger.debug(f"指定仓库地址: {repository_url}")
            return False
    except subprocess.CalledProcessError:
        return False
    finally:
        os.chdir(original_cwd)
