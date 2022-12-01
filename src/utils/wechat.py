import json
from copy import deepcopy
from .cache import cache
from settings import (
    logging,
    URL_ACCESS_TOKEN,
    URL_WECHAT_MESSAGE,
    MAIN_TEMPLATE,
    TEMPLATE_IDS,
    REQUEST_RETRY_COUNT,
    HEFENG_DEFAULT_LOCATION,
)
from .main import request
from .hefeng import get_today_weather


class Wechat:
    @classmethod
    async def get_access_token(cls):
        token = cache.get("access_token")
        if token == None:
            resp = await request(URL_ACCESS_TOKEN)
            token = resp["access_token"]  # type: ignore
            cache.set("access_token", token)
        return token

    @classmethod
    async def push_template_message(cls, data, num=0):
        if num >= REQUEST_RETRY_COUNT:
            return
        token = await cls.get_access_token()
        resp = await request(URL_WECHAT_MESSAGE.format(token), "POST", data=data)
        if resp == None:
            logging.error("模板消息发送失败")
        else:
            if resp["errcode"] == 0:  # type: ignore
                logging.info("微信消息发送成功")
            else:
                logging.debug(f"url:{URL_WECHAT_MESSAGE.format(token)}, data:{data}")
                logging.error(f"模板消息发送失败, 错误信息:{resp['errmsg']}")  # type: ignore
                return await cls.push_template_message(data, num + 1)

    @classmethod
    async def push_message(cls, data: dict, users: list = []):
        if users != []:
            for user in users:
                data["touser"] = user
                await cls.push_template_message(data)
        else:
            await cls.push_template_message(data)

    @classmethod
    async def weather_today(cls, touser_list, location=HEFENG_DEFAULT_LOCATION):
        """多人发送今日天气

        Args:
            touser_list (list): 接收人id列表
        """
        weather = await get_today_weather(location)
        if weather:
            url = weather["fxLink"]
            del weather["fxLink"]
            for touser in touser_list:
                template_msg_data = cls.dispose_template_msg(
                    touser, TEMPLATE_IDS["weather_today"], weather, url
                )
                await cls.push_message(template_msg_data)

    @classmethod
    async def weather_today__location(cls, data: dict):
        """多人发送带地点

        Args:
            data (dict):
        """
        for location, touser_list in data.items():
            await cls.weather_today(touser_list, location)

    @classmethod
    async def create_menu(cls):
        token = await cls.get_access_token()
        menu = json.dumps(
            {
                "button": [
                    {"type": "view", "name": "搜索", "url": "http://www.baidu.com/"},
                    {"type": "view", "name": "日历", "url": "http://rili.xiaoyu.pro/"},
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

    @classmethod
    def dispose_template_msg(cls, touser, template_id, data, url=""):
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


wechat = Wechat
