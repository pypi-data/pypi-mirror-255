## 用户指南

```python
pip3 install PyPoeApi==0.1.6
```

设置账户文件，使用PyPoeApi
```python
from PyPoeApi.poe_client import PoeClient, Chat

PoeClient.ACCOUNT_FILE = ""

async with await PoeClient.create(playground_v2=True) as poe_client:
    chat = Chat()

    image_url = await poe_client.ask(bot_name="Playground-v2",
                                  question="白天，下雨，沙滩，美女，长发，跳舞",
                                  chat=chat)
    print(image_url)

```
ACCOUNT_FILE格式如下
```yaml
accounts:
- Claude-instant-100k: false
  Playground-v2: false
  StableDiffusionXL: false
  formkey: ""
  limit: true
  p_b: ""
date: 2024-02-08
hour: 9
```
其中p_b和formkey是登录的cookie，
通过浏览器或者抓包都可以获取到，
剩下4个bool变量都是用于记录是否限制了，其中
Claude-instant-100k是语言模型，限制30条一天，
Playground-v2是图像模型，限制100条一天，
StableDiffusionXL是图像模型，限制100条一天，
limit是剩余其他大部分模型，总计100条一天。
date和hour分别更新相关的，date指出限制是什么时候，hour指出从什么时候开始更新，
就是把4个bool值变成false，直到触发限制异常就会变成true。


