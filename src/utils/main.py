import re
import json
import asyncio
from tornado.web import RequestHandler
from settings import (
    logging,
    REQUEST_TIMEOUT,
    REQUEST_RETRY_COUNT,
    REQUEST_RETRY_TIMESLEEP,
)
from tornado.simple_httpclient import HTTPTimeoutError
from tornado import httpclient

client = httpclient.AsyncHTTPClient()


class ResponseData:
    def __init__(self) -> None:
        self.code = 200
        self.msg = ""
        self.data = {}


class MiddleHandler(RequestHandler):
    def initialize(self):
        self.data = ResponseData()

    def prepare(self):
        pass

    def finish(self, chunk=None):
        if chunk == None:
            chunk = self.data.__dict__
        super(MiddleHandler, self).finish(chunk)

    def write_error(self, status_code, **kwargs):
        exc_instance = kwargs["exc_info"]
        if status_code != 200:
            self.set_status(status_code)
            self.data.code = status_code
            if self.data.msg == "":
                try:
                    self.data.msg = str(exc_instance[1])
                except:
                    self.data.msg = str(exc_instance)
            self.finish()


class WechatMiddleHandler(MiddleHandler):
    def initialize(self):
        self.wechat = {}
        return super().initialize()

    def prepare(self):
        super().prepare()
        body = self.request.body.decode("utf-8")
        if FromUserName := re.search(r"<FromUserName><!\[CDATA\[(.*?)\]\]></FromUserName>", body):
            if fromUserName := FromUserName.groups()[0]:
                self.wechat["FromUserName"] = fromUserName
            else:
                raise ValueError("没有用户id")
        if Event := re.search(r"<Event><\!\[CDATA\[(.*?)\]]\></Event>", body):
            self.wechat["Event"] = Event.groups()[0]
        if EventKey := re.search(r"<EventKey><\!\[CDATA\[(.*?)\]]\></EventKey>", body):
            self.wechat["EventKey"] = EventKey.groups()[0]
        if Content := re.search(r"<Content><\!\[CDATA\[(.*?)\]]\></Content>", body):
            self.wechat["Content"] = Content.groups()[0]

    def finish(self):
        super(MiddleHandler, self).finish()


async def request(
    url, method="GET", params=None, headers=None, data=None, timeout=REQUEST_TIMEOUT, format="json"
):
    """公共异步请求方法

    Args:
        url (str): url
        method (str, optional): 请求方式. Defaults to "GET".
        params (dict, optional): Defaults to None.
        headers (dict, optional): Defaults to None.
        data (str, optional): Defaults to None.
        timeout (int, optional): Defaults to REQUEST_TIMEOUT.
        format (str, optional): 格式化响应值. Defaults to "json".
    """
    if isinstance(data, dict):
        data = json.dumps(data, ensure_ascii=False)
    if params:
        url += "?"
        for key, value in params.items():
            url += key + "=" + value + "&"
        url = url[:-1]
    httpRequest = httpclient.HTTPRequest(
        url=url, method=method, headers=headers, body=data, request_timeout=timeout
    )
    for _ in range(REQUEST_RETRY_COUNT):
        try:
            response = await client.fetch(httpRequest)
            if response.code == 200:
                if format == "json":
                    return json.loads(response.body.decode("utf-8"))
                else:
                    return response.body
            logging.error(f"请求出错:{url}, code:{response.code}")
            return
        except HTTPTimeoutError:
            logging.warning(f"请求超时:{url}")
        except Exception as e:
            logging.error(f"请求出错:{url}, error:{e}")
        finally:
            await asyncio.sleep(REQUEST_RETRY_TIMESLEEP)
