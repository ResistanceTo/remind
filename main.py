import asyncio
import tornado.web
from urls import urls
from settings import logging, LISTEN_PORT, LISTEN_HOST


async def main():
    app = tornado.web.Application(urls, default_host=LISTEN_HOST)
    app.listen(LISTEN_PORT)
    logging.info("项目已启动: http://{}:{}/".format(LISTEN_HOST, LISTEN_PORT))
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
