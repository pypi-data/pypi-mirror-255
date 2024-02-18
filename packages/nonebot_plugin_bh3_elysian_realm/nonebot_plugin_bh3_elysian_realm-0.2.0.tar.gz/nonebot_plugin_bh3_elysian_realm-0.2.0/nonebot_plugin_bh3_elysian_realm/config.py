from pathlib import Path

from nonebot import get_plugin_config
from pydantic import Extra, BaseSettings


class Config(BaseSettings, extra=Extra.ignore):
    nickname_path: Path = Path(__file__).parent / "resources" / "nickname.json"
    image_path: Path = Path(__file__).parent / "resources" / "images"
    image_repository: str = "https://github.com/MskTmi/ElysianRealm-Data"
    resource_validation_time: int = 60 * 60 * 24
    proxies: str = None
    log_level: str = "INFO"


plugin_config = get_plugin_config(Config)
