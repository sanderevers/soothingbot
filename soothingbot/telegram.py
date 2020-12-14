import logging
from contextlib import asynccontextmanager
from aiohttp import ClientSession

class Telegram:
    def __init__(self,clientSession,config):
        self.clientSession = clientSession
        self.config = config

    async def __ainit__(self):
        url = self.config.register_endpoint.format(apikey=self.config.apikey)
        data = {
            'url': self.config.bot_host + self.config.update_path.format(secret=self.config.apikey),
            'allowed_updates': ['message','callback_query']
        }
        async with self.clientSession.post(url, json=data) as resp:
            json = await resp.json()
            log.debug('{} on webhook register {}: {}'.format(resp.status, data['url'], json))

    async def sendMessage(self,chat_id,text,options=None):
        url = self.config.msg_endpoint.format(apikey=self.config.apikey)
        data = {
            'chat_id':chat_id,
            'text':text,
        }
        if options:
            data['reply_markup']=options
        else:
            data['reply_markup']={'remove_keyboard':True}
        async with self.clientSession.post(url,json=data) as resp:
            json = await resp.json()
            log.debug('sendMessage_resp: {}: {}'.format(resp.status,json))

    async def answerCallbackQuery(self,query_id):
        url = self.config.answerCallbackQuery_endpoint.format(apikey=self.config.apikey)
        data = {
            'callback_query_id': query_id
        }
        async with self.clientSession.post(url,json=data) as resp:
            json = await resp.json()
            log.debug('answerCallbackQuery_resp: {}: {}'.format(resp.status,json))

    async def editMessageText(self,chat_id,msg_id,text):
        url = self.config.editMessageText_endpoint.format(apikey=self.config.apikey)
        data = {
            'chat_id': chat_id,
            'message_id': msg_id,
            'text':text,
            'parse_mode':'MarkdownV2',
            'reply_markup':{}
        }
        async with self.clientSession.post(url,json=data) as resp:
            json = await resp.json()
            log.debug('editMessageText_resp: {}: {}'.format(resp.status,json))


    async def teardown(self):
        url = self.config.register_endpoint.format(apikey=self.config.apikey)
        data = {'url': ''}
        async with self.clientSession.post(url, json=data) as resp:
            json = await resp.json()
            log.debug('{} on webhook deregister: {}'.format(resp.status, json))

    @staticmethod
    @asynccontextmanager
    async def depmanager(deps):
        instance = Telegram(await deps.aget(ClientSession), await deps.aget('config'))
        await instance.__ainit__()
        yield instance
        await instance.teardown()

log = logging.getLogger(__name__)