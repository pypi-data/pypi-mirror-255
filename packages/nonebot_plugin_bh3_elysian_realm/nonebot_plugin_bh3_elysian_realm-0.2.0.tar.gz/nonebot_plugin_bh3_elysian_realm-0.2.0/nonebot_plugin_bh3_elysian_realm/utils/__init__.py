from typing import List
from pathlib import Path

import nonebot_plugin_saa as saa
from nonebot_plugin_saa import TargetQQPrivate
from nonebot import logger, get_bot, get_driver
from nonebot_plugin_apscheduler import scheduler

from nonebot_plugin_bh3_elysian_realm.config import plugin_config
from nonebot_plugin_bh3_elysian_realm.utils.git_utils import git_pull, git_clone, contrast_repository_url
from nonebot_plugin_bh3_elysian_realm.utils.file_utils import (
    check_url,
    load_json,
    save_json,
    merge_dicts,
    list_all_keys,
    list_jpg_files,
    identify_empty_value_keys,
)


class ResourcesVerify:
    image_path: Path = plugin_config.image_path
    image_repository: str = plugin_config.image_repository
    nickname_path: Path = plugin_config.nickname_path
    """资源检查类"""

    def __init__(self):
        self.jpg_list = list_jpg_files(self.image_path)
        self.nickname_cache = load_json(self.nickname_path)

    async def verify_nickname(self):
        """检查nickname.json是否存在"""
        if self.nickname_cache is not None:
            cache: List[str] = list(set(self.jpg_list) - set(await list_all_keys(self.nickname_cache)))
            if not cache:
                logger.info("nickname.json已是最新版本")
                return True
            else:
                logger.warning(f"nickname.json缺少以下角色:{cache}")
                save_json(self.nickname_path, await merge_dicts(self.nickname_cache, {key: [] for key in cache}))
                return False
        else:
            logger.error("nickname.json不存在")
            raise FileNotFoundError

    async def verify_images(self):
        logger.debug("开始检查图片资源")
        logger.debug(f"图片仓库地址: {self.image_repository}")
        logger.debug(f"图片仓库路径: {self.image_path}")
        if await contrast_repository_url(self.image_repository, self.image_path):
            await git_pull(self.image_path)
        else:
            if await git_clone(self.image_repository, self.image_path) is False:
                logger.error("图片资源克隆失败")


@scheduler.scheduled_job("interval", seconds=plugin_config.resource_validation_time, id="resource_validation")
async def resource_scheduled_job():
    logger.debug("开始检查图片资源计划任务")
    await git_pull(plugin_config.image_path)
    await ResourcesVerify().verify_nickname()


@scheduler.scheduled_job("interval", seconds=plugin_config.resource_validation_time, id="null_nickname_warning")
async def null_nickname_warning():
    logger.debug("开始检查nickname.json空值计划任务")
    empty_value_list = await identify_empty_value_keys(load_json(plugin_config.nickname_path))
    if empty_value_list:
        bot = get_bot()
        msg_builder = saa.Text(f"{empty_value_list}缺失昵称，请及时更新")
        logger.debug(f"superusers: {get_driver().config.superusers}")
        for superuser in get_driver().config.superusers:
            msg_target = TargetQQPrivate(user_id=int(superuser))
            await msg_builder.send_to(msg_target, bot)


async def on_startup():
    """启动前检查"""
    await check_url(plugin_config.image_repository, plugin_config.proxies)
    await ResourcesVerify().verify_images()
    await ResourcesVerify().verify_nickname()
    _list = await identify_empty_value_keys(load_json(plugin_config.nickname_path))
    if _list:
        logger.warning(f"{_list}缺失昵称，请及时更新")
