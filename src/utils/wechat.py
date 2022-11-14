import json
from .cache import cache
from settings import logging, URL_ACCESS_TOKEN, URL_WECHAT_MESSAGE
from .main import request


async def get_access_token():
    token = cache.get("access_token")
    if token == None:
        resp = await request(URL_ACCESS_TOKEN)
        token = resp["access_token"]  # type: ignore
        cache.set("access_token", token)
    return token


async def push_message(data: dict):
    token = await get_access_token()
    resp = await request(URL_WECHAT_MESSAGE.format(token), "POST", data=data)
    if resp == None:
        logging.error("模板消息发送失败")
    else:
        if resp["errcode"] == 0:  # type: ignore
            logging.info("微信消息发送成功")
        else:
            logging.error(f"模板消息发送失败, 错误信息:{resp['errmsg']}")  # type: ignore


async def create_menu():
    token = await get_access_token()
    menu = json.dumps(
        {
            "button": [
                {"type": "view", "name": "搜索", "url": "http://www.baidu.com/"},
                {"type": "click", "name": "今日天气", "key": "weather_today"},
            ]
        },
        ensure_ascii=False,
    )
    resp = await request(
        f"https://api.weixin.qq.com/cgi-bin/menu/create?access_token={token}",
        "POST",
        data=menu.encode("utf-8"),
        format="text",
    )
    logging.info(resp)
