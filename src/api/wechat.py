import tornado.ioloop
from src.utils.main import WechatMiddleHandler
from src.utils.hefeng import get_today_weather
from src.utils.wechat import dispose_template_msg, push_message
from settings import TEMPLATE_IDS

async_exec = tornado.ioloop.IOLoop.instance().add_callback


class WechatApiHandler(WechatMiddleHandler):
    async def get(self):
        self.data.msg = self.wechat.get("FromUserName", "")

    async def post(self):
        if self.wechat.get("EventKey") == "weather_today":
            async_exec(self.weather_today, self.wechat.get("FromUserName"))

    async def weather_today(self, touser):
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
