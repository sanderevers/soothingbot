from contextlib import asynccontextmanager
import asyncio

from .chat import Chat
from .telegram import Telegram
from .loadnfa import nfa_from_file

class AppState:
    def __init__(self,telegram,config):
        _self = self
        class Chats(dict):
            def __missing__(self, chat_id):
                self[chat_id] = Chat(chat_id, telegram, _self)
                self[chat_id].start()
                return self[chat_id]

        self.chats = Chats()
        self.nfa_def = nfa_from_file('nfa.json')
        self.msg_count=0

    async def teardown(self):
        chat_closers = [c.stop() for c in self.chats.values()]
        if len(chat_closers) > 0:
            await asyncio.wait(chat_closers)

    @staticmethod
    @asynccontextmanager
    async def depmanager(deps):
        telegram = await deps.aget(Telegram)
        config = await deps.aget('config')
        instance = AppState(telegram,config)
        yield instance
        await instance.teardown()
