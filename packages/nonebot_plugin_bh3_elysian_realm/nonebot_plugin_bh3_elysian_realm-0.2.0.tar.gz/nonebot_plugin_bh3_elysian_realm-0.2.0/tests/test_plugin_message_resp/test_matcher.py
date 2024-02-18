from pathlib import Path

from nonebug import App
from pytest_mock import MockerFixture
from nonebug_saa import should_send_saa
from nonebot import get_driver, get_adapter
from nonebot_plugin_saa import Image, MessageFactory
from nonebot.adapters.onebot.v11 import Bot, Adapter, Message

from .utils import fake_group_message_event_v11


async def test_update_elysian_realm(app: App, mocker: MockerFixture):
    from nonebot_plugin_bh3_elysian_realm.plugins import update_elysian_realm

    mocker.patch.object(get_driver().config, "superusers", {"10"})

    async with app.test_matcher(update_elysian_realm) as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter, auto_connect=False)
        message = Message("/乐土更新")
        event = fake_group_message_event_v11(message=message, sender={"role": "owner"})

        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "更新成功", True)
        ctx.should_finished()


async def test_none_nickname(app: App, mocker: MockerFixture):
    from nonebot_plugin_bh3_elysian_realm.plugins import elysian_realm, plugin_config

    mocker.patch.object(plugin_config, "image_path", Path(Path(__file__).parent / "test_res"))
    mocker.patch.object(plugin_config, "nickname_path", Path(Path(__file__).parent / "test_res" / "test_nickname.json"))

    async with app.test_matcher(elysian_realm) as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter, auto_connect=False)
        message = Message("/乐土人人")
        event = fake_group_message_event_v11(message=message)

        ctx.receive_event(bot, event)
        ctx.should_call_send(event, "未找到指定角色: 人人", True)
        ctx.should_finished()


async def test_elysian_realm(app: App, mocker: MockerFixture):
    from nonebot_plugin_bh3_elysian_realm.plugins import elysian_realm, plugin_config

    mocker.patch.object(plugin_config, "image_path", Path(Path(__file__).parent.parent / "test_res"))
    mocker.patch.object(
        plugin_config, "nickname_path", Path(Path(__file__).parent.parent / "test_res" / "test_nickname.json")
    )

    async with app.test_matcher(elysian_realm) as ctx:
        adapter = get_adapter(Adapter)
        bot = ctx.create_bot(base=Bot, adapter=adapter, auto_connect=False)
        message = Message("/乐土人律")
        event = fake_group_message_event_v11(message=message)

        ctx.receive_event(bot, event)
        should_send_saa(
            ctx,
            MessageFactory(Image(Path(__file__).parent.parent / "test_res" / "Human.jpg")),
            bot,
            event=event,
        )
        ctx.should_finished()
