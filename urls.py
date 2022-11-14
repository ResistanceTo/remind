from src.api.main import MainHandler
from src.api.wechat import WechatApiHandler

urls = [
    (r"/?", MainHandler),
    (r"/api/wechat/?", WechatApiHandler),
]
