from aiohttp import web
from .exceptions import AbortRequestException
from .appstate import AppState
from .loadnfa import process
import logging

class Routes:
    def __init__(self,config):
        self.config = config

    async def recv_updates(self,req):
        if req.match_info['secret'] != self.config.apikey:
            raise AbortRequestException()

        state = await req.app['d'].aget(AppState)
        update = await req.json()
        logging.debug(str(update))

        if update.get('message'):
            msg =  update.get('message')
            text = msg['text']
            chat_id = msg['chat']['id']
            chat = state.chats[chat_id]
            await chat.dispatch(text)
        elif update.get('callback_query'):
            query = update.get('callback_query')
            chat_id = query['message']['chat']['id']
            msg_id = query['message']['message_id']
            chat = state.chats[chat_id]
            personality = query['data']
            await chat.dispatch(f'/callback {msg_id} {query["id"]} {personality}')
        return web.Response(status=200)

    async def recv_nfa(self,req):
        if req.match_info['secret'] != self.config.apikey:
            raise AbortRequestException()

        state = await req.app['d'].aget(AppState)
        graph = await req.json()
        logging.debug(str(graph))
        state.nfa_def = process(graph)

        return web.Response(status=200)

    async def stats(self,req):
        state = await req.app['d'].aget(AppState)
        text = f'#chats: {len(state.chats)}\n#msgs: {state.msg_count}'
        return web.Response(text=text,status=200)

log = logging.getLogger(__name__)