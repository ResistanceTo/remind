import json
from copy import deepcopy
from .cache import cache
from settings import (
    logging,
    URL_ACCESS_TOKEN,
    URL_WECHAT_MESSAGE,
    MAIN_TEMPLATE,
    TEMPLATE_IDS,
)
from .main import request
from .hefeng import get_today_weather


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


async def weather_today(touser):
    """发送今日天气

    Args:
        touser (str): 接收人id
    """
    weather = await get_today_weather()
    if weather:
        url = weather["fxLink"]
        del weather["fxLink"]
        template_msg_data = dispose_template_msg(
            touser, TEMPLATE_IDS["weather_today"], weather, url
        )
        await push_message(template_msg_data)


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


def dispose_template_msg(touser, template_id, data, url=""):
    """构建模板消息

    Args:
        touser (str): 要发送给的人
        template_id (str): 模板id
        data (dict): 消息体数据
        url (str, optional): 可跳转到的链接. Defaults to "".
    """
    msg_data = {}
    for key, value in data.items():
        msg_data[key] = {"value": value, "color": "#173177"}
    template = deepcopy(MAIN_TEMPLATE)
    template["touser"] = touser
    template["template_id"] = template_id
    template["url"] = url
    template["data"] = msg_data
    return template
