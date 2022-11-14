from .main import request
from settings import logging, HEFENG_DEFAULT_LOCATION, HEFENG_KEY, HEFENG_URL_3D


async def get_today_weather(location=HEFENG_DEFAULT_LOCATION):
    """获取今日天气

    Args:
        location (str, optional): 城市编码,默认北京. Defaults to HEFENG_DEFAULT_LOCATION.
    """
    params = {"location": location, "key": HEFENG_KEY}
    resp = await request(HEFENG_URL_3D, params=params)
    if resp["code"] == "400":  # type: ignore
        return
    if not resp:
        logging.error("请求天气接口出错")
        logging.debug(f"params = {params}")
    else:
        res = resp["daily"][0]  # type: ignore
        res["fxLink"] = resp["fxLink"]  # type: ignore
        return res
