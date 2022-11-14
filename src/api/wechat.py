from src.utils.main import WechatMiddleHandler


class SendTemplateMsgHandler(WechatMiddleHandler):
    async def get(self):
        self.data.msg = self.wechat.get("FromUserName", "")
