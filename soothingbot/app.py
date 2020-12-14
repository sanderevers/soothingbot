import asyncio
import logging
from aiohttp import web, ClientSession
from contextlib import asynccontextmanager

from .exceptions import AbortRequestException
from .routes import Routes
from .appstate import AppState
from .telegram import Telegram
from outhouse import DependencyProvider

def create(config):
    app = web.Application(middlewares=[exception_mapper])
    d = DependencyProvider()
    app['d'] = d
    d.register('config',lambda x: x,config)
    d.register(ClientSession,initmanager,ClientSession)
    d.register(AppState,AppState.depmanager,d)
    d.register(Telegram,Telegram.depmanager,d)
    app.on_startup.append(init_routes)
    app.on_startup.append(warmup_telegram)
    app.on_shutdown.append(teardown_deps)
    return app

async def warmup_telegram(app):
    await app['d'].aget(Telegram)

async def init_routes(app):
    config = await app['d'].aget('config')
    routes = Routes(config)
    app.add_routes([
        web.post(config.update_path, routes.recv_updates),
        web.post('/bot/{secret}/nfa', routes.recv_nfa),
        web.get('/bot/{secret}/stats', routes.stats)
    ])

async def teardown_deps(app):
    await app['d'].async_teardown()

@web.middleware
async def exception_mapper(request,handler):
    try:
        resp = await handler(request)
        return resp
    except AbortRequestException as e:
        return web.Response(status=e.status, text=e.text)


@asynccontextmanager
async def initmanager(cls):
    inst = cls()
    yield inst
    await inst.close()
    await asyncio.sleep(0.250) #see https://github.com/aio-libs/aiohttp/issues/1925


log = logging.getLogger(__name__)

