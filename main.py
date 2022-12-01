import asyncio
import tornado.web
from urls import urls
from aiotorndb import Connection
from settings import (
    logging,
    LISTEN_PORT,
    LISTEN_HOST,
    SCHED_MINUTE,
    SCHED_HOUR,
    WHITELIST,
    DB_HOST,
    DB_PORT,
    DB_DATABASE,
    DB_USER,
    DB_PASSWORD,
    LOCATION_WHITELIST,
    USERS_LOCATION
)
from src.utils.wechat import wechat
from apscheduler.schedulers.asyncio import AsyncIOScheduler

sched = AsyncIOScheduler()


async def initialization():
    DB = Connection(
        host=DB_HOST,
        db=DB_DATABASE,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        time_zone="+8:00",
        charset="utf8",
    )

    users = await DB.select("SELECT userid, location from usermodel where white = 1")
    for user in users:
        WHITELIST.add(user["userid"])
        USERS_LOCATION[user["userid"]] = user["location"]
    logging.info("初始化完毕")


async def main():
    await initialization()
    app = tornado.web.Application(urls, default_host=LISTEN_HOST)
    app.listen(LISTEN_PORT)
    logging.info("项目已启动: http://{}:{}/".format(LISTEN_HOST, LISTEN_PORT))
    sched.add_job(
        wechat.weather_today,
        "cron",
        args=[WHITELIST],
        minute=SCHED_MINUTE,
        hour=SCHED_HOUR,
    )
    sched.start()
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
