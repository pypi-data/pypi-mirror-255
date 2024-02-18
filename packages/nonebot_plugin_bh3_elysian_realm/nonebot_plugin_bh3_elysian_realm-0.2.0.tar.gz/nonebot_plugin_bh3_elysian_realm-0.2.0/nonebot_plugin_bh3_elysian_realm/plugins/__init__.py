from pathlib import Path

import nonebot_plugin_saa as saa
from nonebot.typing import T_State
from nonebot.matcher import Matcher
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot import logger, on_command
from nonebot.permission import SUPERUSER
from nonebot.internal.params import ArgPlainText

from nonebot_plugin_bh3_elysian_realm.config import plugin_config
from nonebot_plugin_bh3_elysian_realm.utils.file_utils import string_to_list, find_key_by_value
from nonebot_plugin_bh3_elysian_realm.utils import git_pull, load_json, save_json, identify_empty_value_keys

elysian_realm = on_command("乐土攻略", aliases={"乐土", "乐土攻略"}, priority=7)
update_elysian_realm = on_command("乐土更新", aliases={"乐土更新"}, priority=7, permission=SUPERUSER)
add_nickname = on_command("添加乐土昵称", aliases={"添加乐土昵称"}, priority=7, permission=SUPERUSER)


@elysian_realm.handle()
async def handle_first_receive(matcher: Matcher, args: Message = CommandArg()):
    if args.extract_plain_text():
        matcher.set_arg("role", args)


@elysian_realm.got("role", prompt="请指定角色")
async def got_introduction(role: str = ArgPlainText()):
    nickname = await find_key_by_value(load_json(plugin_config.nickname_path), role)
    if nickname is None:
        await elysian_realm.finish(f"未找到指定角色: {role}")
    else:
        msg_builder = saa.Image(Path(plugin_config.image_path / f"{nickname}.jpg"))
        await msg_builder.finish()


@update_elysian_realm.handle()
async def _(matcher: Matcher, args: Message = CommandArg()):
    await update_elysian_realm.finish("更新成功" if await git_pull(plugin_config.image_path) else "更新失败")


@add_nickname.handle()
async def _handle_first_receive(state: T_State):
    state["nickname_cache"] = load_json(plugin_config.nickname_path)
    empty_value_list = await identify_empty_value_keys(state["nickname_cache"])
    if empty_value_list:
        logger.debug("nickname.json存在没有昵称的图片")
        msg_builder = saa.Text(f"nickname.json空值列表: {empty_value_list}\n以上为没有昵称的图片文件名")
    else:
        msg_builder = saa.Text("nickname.json不存在没有昵称的图片")

    await msg_builder.send()


@add_nickname.got("filename", prompt="图片文件名")
@add_nickname.got("nickname", prompt="昵称")
async def _(state: T_State, filename: str = ArgPlainText("filename"), nickname: str = ArgPlainText("nickname")):
    logger.debug(f"filename: {filename}\nnickname: {nickname}")
    state["filename"] = filename
    state["nicknames"] = string_to_list(nickname)
    if filename not in state["nickname_cache"]:
        msg_builder = saa.Text(f"未找到图片文件: {filename}")
        await msg_builder.reject_arg("filename")
    elif not state["nickname_cache"][filename]:
        state["nickname_cache"][filename] = state["nicknames"]
        save_json(plugin_config.nickname_path, state["nickname_cache"])
        msg_builder = saa.Text(f"已更新\n{filename}: {nickname}")
        await msg_builder.finish()
    else:
        for nickname in state["nicknames"]:
            state["nickname_cache"][filename].append(nickname)
        save_json(plugin_config.nickname_path, state["nickname_cache"])
        msg_builder = saa.Text(f"添加成功\n{filename}: {state['nickname_cache'][filename]}")
        await msg_builder.finish()
