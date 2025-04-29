
from aiohttp import web
import aiohttp_jinja2
import jinja2

async def create_web_app():
    app = web.Application()
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('../templates'))
    return app

async def start_web_server(app):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
