import asyncio
import tornado.web
from urls import urls
from settings import logging, LISTEN_PORT, LISTEN_HOST, SCHED_MINUTE, SCHED_HOUR
from src.utils.wechat import weather_today
from apscheduler.schedulers.asyncio import AsyncIOScheduler

sched = AsyncIOScheduler()


async def main():
    app = tornado.web.Application(urls, default_host=LISTEN_HOST)
    app.listen(LISTEN_PORT)
    logging.info("项目已启动: http://{}:{}/".format(LISTEN_HOST, LISTEN_PORT))
    sched.add_job(weather_today, "cron", minute=SCHED_MINUTE, hour=SCHED_HOUR)
    sched.start()
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
