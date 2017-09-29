import zlib
import requests
import time
import websocket
import json
import queue
from concurrent.futures import ThreadPoolExecutor

__all__ = ["PandaTvDanmakuClient"]


class PandaTvDanmakuClient(object):
    """
    熊猫TV Python3 WebSocket弹幕客户端
    """

    def __init__(self):
        self._roomid = None
        self._tp = None
        self._ssl = None
        self._data = None
        self._ws = None
        self._ws_url = None
        self._queue = None
        self._beatConn = None
        self._is_close = None

    def _beat(self):
        t = int(time.time())
        while not self._is_close:
            time.sleep(1)
            if int(time.time()) - t > 30:
                self._ws.send(bytes.fromhex('00060000'), opcode=websocket.ABNF.OPCODE_BINARY)
                t = int(time.time())

    def _init_conn(self, _ws):
        head = bytes.fromhex('00060002009b')
        body = bytes("u:%s@%s\n"
                     "ts:%s\n"
                     "sign:%s\n"
                     "authtype:4\n"
                     "plat:jssdk_pc_web\n"
                     "version:0.5.9\n"
                     "pdft:\n"
                     "network:unknown\n"
                     "compress:zlib" %
                     (self._data['rid'], self._data['appid'],
                      self._data['ts'], self._data['sign']), encoding='utf-8')
        _ws.send(head + body, opcode=websocket.ABNF.OPCODE_BINARY)
        self._beatConn = self._tp.submit(self._beat)

    def _parse(self, _ws, mess):
        if len(mess) < 5:
            return
        try:
            ext = zlib.decompress(mess[15:])
            self._queue.put(json.loads(ext[16:]), block=False)
        except Exception:
            pass

    def _run(self):
        self._ws = websocket.WebSocketApp(url=('wss://' if self._ssl else 'ws://') + self._ws_url,
                                          on_open=self._init_conn,
                                          on_message=self._parse)
        self._ws.run_forever(origin='http://www.panda.tv')

    def subscribe(self, roomid, tp=ThreadPoolExecutor(4), ssl=True) -> queue.Queue:
        """
        订阅直播间弹幕数据
        :param roomid: 房间id
        :param tp: 线程池
        :param ssl: 是否使用SSL
        :return: 弹幕数据队列
        """
        if not isinstance(roomid, int):
            raise RuntimeError('room id must be int.')
        self._roomid = roomid
        self._tp = tp
        self._ssl = ssl
        url = 'https://riven.panda.tv/chatroom/getinfo'
        data = requests.get(url, params={
            'roomid': self._roomid,
            'app': 1,
            'protocol': 'ws',
            '_caller': 'panda-pc_web',
            '__plat': 'pc_web',
            '_': int(time.time())
        }).json()
        if data['errno'] != 0:
            raise RuntimeError('room id: %s can`t find', str(self._roomid))
        self._data = data['data']
        self._ws_url = list(filter(lambda i: ('443' if self._ssl else '8080') in i, self._data['chat_addr_list']))[0]
        self._queue = queue.Queue()
        self._is_close = False
        return self._queue

    def run(self) -> None:
        """
        正式启动，开始接受数据
        """
        if not self._ws:
            self._tp.submit(self._run)

    def close(self) -> None:
        """
        关闭连接
        """
        if self._ws and not self._is_close:
            self._is_close = True
            self._ws.close()
