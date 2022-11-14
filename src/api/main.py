from src.utils.main import MiddleHandler


class MainHandler(MiddleHandler):
    async def get(self):
        self.data.msg = "Hello world, [get]"

    async def post(self):
        self.data.msg = "test"
        self.data.code = 123
