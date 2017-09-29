# PandaTvDanmakuClient
熊猫TV WebSocket 协议弹幕客户端
## 依赖
* Python 3
* [websocket-client](https://github.com/websocket-client/websocket-client)
* [requests](https://github.com/requests/requests)
## 使用
```python
from PandaTvDanmakuClient import PandaTvDanmakuClient

panda = PandaTvDanmakuClient()
queue = panda.subscribe(10300)
panda.run()
try:
    while 1:
        data = queue.get()
        print(data)
except KeyboardInterrupt:
    pass
finally:
        panda.close()
```
## 输出
队列为无界队列，包含字典对象，包含弹幕和礼物等信息，需要什么字段自己拿就好了
```json
{ 
    "type" : "1", 
    "time" : 1506650124, 
    "data" : {
        "from" : {
            "identity" : "30", 
            "nickName" : "打他吗呢香蕉牛奶", 
            "badge" : "", 
            "rid" : "40998904", 
            "msgcolor" : "", 
            "level" : "7", 
            "sp_identity" : "30", 
            "__plat" : "android", 
            "userName" : ""
        }, 
        "to" : {
            "toroom" : "404055"
        }, 
        "content" : "mini变强了"
    }
}
```
