# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_bard']

package_data = \
{'': ['*'], 'nonebot_plugin_bard': ['images/*']}

install_requires = \
['bardapi>=0.1.39,<0.2.0',
 'nonebot-adapter-onebot>=2.2.1,<3.0.0',
 'nonebot2>=2.0.0rc3,<3.0.0',
 'websocket-client>=1.6.1,<2.0.0']

setup_kwargs = {
    'name': 'nonebot-plugin-bard',
    'version': '0.2.0',
    'description': 'A nonebot plugin for Bard',
    'long_description': '<div align="center">\n  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>\n  <br>\n  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>\n</div>\n\n<div align="center">\n\n# nonebot-plugin-bard\n</div>\n\n# 介绍\n- 本插件是适配Google Bard模型的聊天机器人插件，借助bard的联网能力和多模态识别能力实现更准确地回复和图片识别回复等功能。\n- 目前中文回答和英文回答使用的模型均为Gemini Pro\n- ![Gemini Pro的联网能力](nonebot_plugin_bard/images/demo2.jpg)\n- ![Gemini Pro的多模态识别能力](nonebot_plugin_bard/images/demo1.jpg)\n# 安装\n\n* 手动安装\n  ```\n  git clone https://github.com/Alpaca4610/nonebot_plugin_bard.git\n  ```\n\n  下载完成后在bot项目的pyproject.toml文件手动添加插件：\n\n  ```\n  plugin_dirs = ["xxxxxx","xxxxxx",......,"下载完成的插件路径/nonebot_plugin_bard"]\n  ```\n* 使用 pip\n  ```\n  pip install nonebot-plugin-bard\n  ```\n\n# 配置文件\n\n## 必选内容\n在Bot根目录下的.env文件中填入Bard的cookies信息：\n```\nbard_token = xxxxxxxx\n```\n<a id=\'cookies\'></a>\n### cookies获取方法\n0. 确保您已经拥有bard的访问权限\n1. 访问 https://bard.google.com/\n2. 按 F12 打开控制台，进入应用程序(Application) → Cookies → 复制 ```__Secure-1PSID``` 的值，注意不要包含```__Secure-1PSID```本身\n3. cookies过一段时间可能会失效，如有报错更新即可\n\n##  可选内容：\n```\nbard_enable_private_chat = True   # 私聊开关，默认开启，改为False关闭\nbard_proxy = "127.0.0.1:8001"    # 配置代理访问Bard\n```\n若配置了bard_token还无法访问bard，请额外增加两项cookies信息，bard_token也需要配置）\n```\nbard_token1 = "xxxxxxxx"  # "__Secure-1PSIDTS"的值\nbard_token2 = "xxxxxxxx"  # "__Secure-1PSIDCC"的值\n```\n\n# 使用方法\n- bard+文字 发起无记忆对话\n- bard+图片 调用bard的多模态识别能力识图\n',
    'author': 'Alpaca',
    'author_email': 'alpaca@bupt.edu.cn',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
