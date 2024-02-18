<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot_plugin_bh3_elysian_realm

_✨ BH3 Elysian Realm bot power by NoneBot2 ✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/BalconyJH/nonebot_plugin_bh3_elysian_realm.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot_plugin_bh3_elysian_realm">
    <img src="https://img.shields.io/pypi/v/nonebot_plugin_bh3_elysian_realm.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">
<img src="https://img.shields.io/badge/nonebot-2.0+-blue.svg" alt="nonebot">
<img src="https://img.shields.io/codecov/c/github/balconyjh/nonebot_plugin_bh3_elysian_realm" alt="codecov">

</div>

## 📖 介绍

崩坏3乐土攻略插件

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot_plugin_bh3_elysian_realm

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot_plugin_bh3_elysian_realm

</details>
<details>
<summary>pdm</summary>

    pdm add nonebot_plugin_bh3_elysian_realm

</details>
<details>
<summary>poetry</summary>

    poetry add nonebot_plugin_bh3_elysian_realm

</details>
<details>
<summary>conda</summary>

    conda install nonebot_plugin_bh3_elysian_realm

</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_bh3_elysian_realm"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

|   配置项   | 必填 | 默认值 |   说明   |
| :--------: | :--: | :----: | :------: |
| SUPERUSERS |  是  |   无   | 超级用户 |

## 🎉 使用

### 指令表

|     指令     |    权限    | 需要@ |   范围    |         说明         |
| :----------: | :--------: | :---: | :-------: | :------------------: |
|   乐土攻略   |    群员    |  否   |   群聊    |   指定角色乐土攻略   |
|   乐土更新   | SUPERUSERS |  否   | 群聊/私聊 | 更新乐土攻略图片资源 |
| 添加乐土昵称 | SUPERUSERS |  否   | 群聊/私聊 |   添加乐土角色昵称   |

### 效果图

#### 乐土攻略

![乐土攻略](/document/images/1.png)

#### 乐土更新

![乐土更新](/document/images/2.png)

#### 添加乐土昵称

![添加乐土昵称](/document/images/3.png)

## 📊 统计

![Alt](https://repobeats.axiom.co/api/embed/289170c6a60d07bc11449873640985d779cd9be1.svg "Repobeats analytics image")

## 📄 许可证

Code: AGPL-3.0 - 2023 - BalconyJH

## 🪜 鸣谢

### 插件依赖 [ElysianRealm-Data](https://github.com/MskTmi/ElysianRealm-Data) 提供攻略图片。

### 插件依赖 [Bh3-ElysianRealm-Strategy](https://github.com/MskTmi/Bh3-ElysianRealm-Strategy) 提供灵感来源。

### 插件框架 [NoneBot2](https://github.com/nonebot/nonebot2) 提供插件开发框架。

感谢以下开发者作出的贡献：

<a href="https://github.com/BalconyJH/nonebot_plugin_bh3_elysian_realm/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=BalconyJH/nonebot_plugin_bh3_elysian_realm" />
</a>
