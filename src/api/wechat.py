import tornado.ioloop
from src.utils.main import WechatMiddleHandler
from src.utils.wechat import weather_today


class WechatApiHandler(WechatMiddleHandler):
    async def get(self):
        self.data.msg = self.wechat.get("FromUserName", "")

    async def post(self):
        if self.wechat.get("EventKey") == "weather_today":
            tornado.ioloop.IOLoop.instance().add_callback(
                weather_today, self.wechat.get("FromUserName")
            )
