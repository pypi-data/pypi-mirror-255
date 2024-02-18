from nonebot import require, get_driver

require("nonebot_plugin_apscheduler")
require("nonebot_plugin_localstore")
require("nonebot_plugin_saa")

from nonebot.plugin import PluginMetadata, inherit_supported_adapters

from nonebot_plugin_bh3_elysian_realm.utils import on_startup

from .config import plugin_config
from . import plugins  # noqa: F401

driver = get_driver()

__plugin_meta__ = PluginMetadata(
    name="乐土攻略",
    description="崩坏3乐土攻略",
    type="application",
    usage="""
    [乐土XX] 指定角色乐土攻略
    [乐土更新] 更新乐土攻略图片资源
    [添加乐土昵称] 添加乐土角色昵称
    """.strip(),
    extra={
        "author": "BalconyJH <balconyjh@gmail.com>",
    },
    supported_adapters=inherit_supported_adapters("nonebot_plugin_saa"),
)


@driver.on_startup
async def _():
    """启动前检查"""
    if plugin_config.log_level == "DEBUG":
        return
    await on_startup()
