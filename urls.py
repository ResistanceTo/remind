from src.api.main import MainHandler

urls = [
    (r"/?", MainHandler),
    (r"/send/?", MainHandler),
]
