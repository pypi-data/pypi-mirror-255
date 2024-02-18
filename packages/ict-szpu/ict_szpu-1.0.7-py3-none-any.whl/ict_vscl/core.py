import asyncio
import json
import sys
import threading
import time

import websocket

Version = '1.0'
# 常量
SUCCESS = 1
FAILED_WARNING = 2
FAILED_ERROR = 3


# sdk底层核心
class Core:
    ws = None
    asyncEvects = {}  # 异步事件
    resultEvents = {}  # 异步结果
    eventId = 0  # 等待事件id
    loop = None

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.init())

    def om_open(self, ws):
        print('连接虚仿端成功')
        self.sendmsg(json.dumps({'event_id': 0, 'type': 'checkSdk', 'data': Version}))

    # 定义一个用来接收监听数据的方法
    def on_message(self, ws, message: str):
        # print("监听到消息,内容如下：" + message)
        obj = json.loads(message)
        id = obj['event_id']
        if id == None:
            print("主动消息:" + obj['msg'])
        else:
            self.resultEvents[id] = obj
            self.loop.call_soon_threadsafe(lambda: self.call(id))

    def call(self, id: int):
        if id in self.asyncEvects.keys():
            self.asyncEvects[id].set()
            del self.asyncEvects[id]
        else:
            print('无此id' + str(id))

    # 定义一个用来处理错误的方法
    def on_error(self, ws, error):
        print("-----连接出现异常，异常信息如下-----")
        print(error)

    # 定义一个用来处理关闭连接的方法
    def on_close(self, ws, code, msg):
        print("-------连接已关闭------")
        print(code)

    def sendmsg(self, msg: str):
        self.ws.send(msg)

    def run(self):
        time.sleep(1)
        # print('启动监听')
        self.ws.run_forever()

    async def init(self):
        print('初始化中...')
        self.ws = websocket.WebSocketApp("ws://127.0.0.1:10088/cxx",
                                         on_open=self.om_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close,
                                         )

        self.eventId = 0
        self.asyncEvects[0] = asyncio.Event()

        thread = threading.Thread(target=self.run)
        thread.daemon = True
        thread.start()
        await self.asyncEvects[0].wait()
        print('sdk版本检查中...')
        obj = self.resultEvents[0]
        del self.resultEvents[0]
        # 检查sdk版本
        if obj['result'] == SUCCESS:
            print("sdk版本正确")

            # 场景初始化
            print('场景初始化中...')
            self.eventId = 1
            self.asyncEvects[1] = asyncio.Event()
            self.sendmsg(json.dumps({'event_id': 1, 'type': 'other', 'commond': 'init_scene'}))
            await self.asyncEvects[1].wait()
            obj2 = self.resultEvents[1]
            del self.resultEvents[1]
            if obj2['result'] == SUCCESS:
                print('场景初始化成功')
            else:
                print('场景初始化失败:' + obj2.get('msg'))
        else:
            print("sdk版本不匹配! 请更换版本，当前版本：" + Version)
            sys.exit()

    def do_wait_return(self, data: dict):
        """
        发送消息并等待Unity程序返回结果
        :param data:
        """
        result = self.loop.run_until_complete(self.send_wait_return(data))

        if result['result'] != FAILED_ERROR:
            # if result.get('msg') is not None:
            #     print(result.get('msg'))
            return result
        else:
            print(result.get('msg'))
            sys.exit()

    def do_immediately(self, data: dict):
        """
        发送消息不等待Unity程序返回结果
        :param data:
        :return:
        """
        asyncio.run(self.send_no_return(data))

    async def send_wait_return(self, data: dict):
        self.eventId += 1
        __id = self.eventId
        data['event_id'] = __id
        self.asyncEvects[__id] = asyncio.Event()
        self.sendmsg(json.dumps(data))
        # print('开始等待事件%s结束' % __id)
        await Core.asyncEvects[__id].wait()
        obj = self.resultEvents[__id]
        del self.resultEvents[__id]
        return obj

    async def send_no_return(self, data: dict):
        self.eventId += 1
        __id = self.eventId
        data['event_id'] = __id
        self.asyncEvects[__id] = asyncio.Event()
        self.sendmsg(json.dumps(data))


MyWS = Core()
