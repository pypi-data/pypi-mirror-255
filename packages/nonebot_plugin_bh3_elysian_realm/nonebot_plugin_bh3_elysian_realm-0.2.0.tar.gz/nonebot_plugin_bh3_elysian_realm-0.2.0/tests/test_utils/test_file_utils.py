import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest


class TestLoadJsonFiles(unittest.TestCase):
    def test_load_empty_file(self):
        from nonebot_plugin_bh3_elysian_realm.utils.file_utils import load_json

        with NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
            path = Path(tmp_file.name)
            assert load_json(path) == {}

    def test_load_valid_json(self):
        from nonebot_plugin_bh3_elysian_realm.utils.file_utils import load_json

        file = Path(__file__).parent.parent / "test_res" / "test_nickname.json"
        assert load_json(file) != {}

    def test_file_not_found(self):
        from nonebot_plugin_bh3_elysian_realm.utils.file_utils import load_json

        path = Path("/path/to/non/existent/file.json")
        result = load_json(path)
        assert result == {}, "应当返回空字典当文件不存在"


class TestSaveJsonFiles(unittest.TestCase):
    def test_save_empty_dict(self):
        from nonebot_plugin_bh3_elysian_realm.utils.file_utils import load_json, save_json

        with NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
            path = Path(tmp_file.name)
            save_json(path, {})
            assert load_json(path) == {}

    def test_save_valid_json(self):
        from nonebot_plugin_bh3_elysian_realm.utils.file_utils import load_json, save_json

        file = Path(__file__).parent.parent / "test_res" / "test_nickname.json"
        data = load_json(file)
        with NamedTemporaryFile(delete=False, suffix=".json") as tmp_file:
            path = Path(tmp_file.name)
            save_json(path, data)
            assert load_json(path) == data

    def test_file_not_found(self):
        from nonebot_plugin_bh3_elysian_realm.utils.file_utils import save_json

        path = Path(__file__).parent / "test_res" / "test_nickname.json"
        with pytest.raises(FileNotFoundError):
            save_json(path, {})


class TestListJpgFiles(unittest.TestCase):
    def test_list_jpg_files(self):
        from nonebot_plugin_bh3_elysian_realm.utils.file_utils import list_jpg_files

        path = Path(__file__).parent.parent / "test_res"
        assert list_jpg_files(path) == ["Human"]


class TestStringToList(unittest.TestCase):
    def test_string_to_list(self):
        from nonebot_plugin_bh3_elysian_realm.utils.file_utils import string_to_list

        assert string_to_list("a, b, c") == ["a", "b", "c"]
        assert string_to_list("a,b,c") == ["a", "b", "c"]
        assert string_to_list("a, b,c") == ["a", "b", "c"]
        assert string_to_list("a,b, c") == ["a", "b", "c"]
        assert string_to_list("a,b") == ["a", "b"]
        assert string_to_list("a") == ["a"]
        assert string_to_list("") == []
        assert string_to_list(" ") == []


class TestFindKeyByValue(unittest.TestCase):
    async def test_find_key_by_value(self):
        from nonebot_plugin_bh3_elysian_realm.utils.file_utils import load_json, find_key_by_value

        data = load_json(Path(__file__).parent.parent / "test_res" / "test_nickname.json")
        assert await find_key_by_value(data, "人律") == "Human"
        assert await find_key_by_value(data, "人人") is None


@pytest.mark.asyncio
async def test_identify_empty_value_keys():
    from nonebot_plugin_bh3_elysian_realm.utils.file_utils import load_json, identify_empty_value_keys

    data = load_json(Path(__file__).parent.parent / "test_res" / "test_nickname.json")
    assert await identify_empty_value_keys(data) == ["Vicissitude_Attack"]


@pytest.mark.asyncio
async def test_list_all_keys():
    from nonebot_plugin_bh3_elysian_realm.utils.file_utils import load_json, list_all_keys

    data = load_json(Path(__file__).parent.parent / "test_res" / "test_nickname.json")
    assert await list_all_keys(data) == [
        "Human",
        "CosmicExpression_Mixed",
        "Vicissitude_Attack",
    ]


@pytest.mark.asyncio
async def test_merge_dicts():
    from nonebot_plugin_bh3_elysian_realm.utils.file_utils import load_json, merge_dicts

    data = load_json(Path(__file__).parent.parent / "test_res" / "test_nickname.json")
    assert await merge_dicts(data, {"test": ["test"]}) == {
        "Human": ["人律", "爱律"],
        "Vicissitude_Attack": [],
        "CosmicExpression_Mixed": ["大格蕾修混合流"],
        "test": ["test"],
    }


@pytest.mark.asyncio
async def test_merge_dicts_with_update():
    from nonebot_plugin_bh3_elysian_realm.utils.file_utils import load_json, merge_dicts

    data = load_json(Path(__file__).parent.parent / "test_res" / "test_nickname.json")
    assert await merge_dicts(data, {"Human": ["老婆"]}) == {
        "Human": ["老婆"],
        "Vicissitude_Attack": [],
        "CosmicExpression_Mixed": ["大格蕾修混合流"],
    }


@pytest.mark.asyncio
async def test_check_url():
    from nonebot_plugin_bh3_elysian_realm.config import plugin_config
    from nonebot_plugin_bh3_elysian_realm.utils.file_utils import check_url

    assert await check_url(plugin_config.image_repository, plugin_config.proxies) is True
