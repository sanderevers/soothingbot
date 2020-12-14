import logging
import asyncio
import random
from .task import Task
from .loadnfa import nfa_from_file
from .nfa import run
from .finitequeue import FiniteQueue
from .composite_emoji import split_emoji

class Chat(Task):
    def __init__(self,chat_id,telegram,appstate):
        super().__init__()
        self.chat_id = chat_id
        self.telegram = telegram
        self.appstate = appstate
        self.inq = FiniteQueue()
        self.personality = Personality.Chatty

    async def _run(self):
        nfa = None
        async for text in self.inq:
            self.appstate.msg_count+=1
            cmd,args= parse(text)
            try:
                if cmd=='personality':
                    if args:
                        self.personality = Personality.of(args[0])
                    else:
                        await self.askPersonality()
                        continue
                elif cmd=='callback':
                    [msg_id, query_id,new_personality] = args
                    text = Personality.text(self.personality)
                    if new_personality!=text:
                        text=f'~{text}~ {new_personality}'
                    self.personality = Personality.of(new_personality)

                    await self.telegram.answerCallbackQuery(query_id)
                    await self.telegram.editMessageText(self.chat_id,msg_id,text)
                elif cmd=='reset' or cmd=='start':
                    nfa = None
                else:
                    theirsyms = split_emoji(args)
            except Exception as e:
                log.debug(e)

            if not nfa:
                d,start,end = self.appstate.nfa_def
                nfa = run(d,start,end)
                accepting, syms = nfa.send(None)
                theirsyms = []

            if theirsyms and not (len(syms)==0 and theirsyms==['🙂']):
                accepting,syms = self.do_theirs(nfa,theirsyms)
            accepting,syms,oursyms = self.do_ours(nfa,accepting,syms)

            text = oursyms or ('🙂' if accepting else '️🧐' if len(syms) else '😔️')
            their_choices = syms or (['🙂', '/reset'] if accepting else ['😔️', '/reset'])
            await self.reply(text,their_choices)

    def do_theirs(self,nfa,theirsyms):
        for theirsym in theirsyms:
            try:
                accepting, syms = nfa.send(theirsym)
            except StopIteration:
                accepting, syms = False, set()
        return accepting,syms

    def do_ours(self,nfa,accepting,syms):
        oursyms = ''
        for _ in range(nreplies(self.personality)):
            try:
                oursym = random.choice(list(syms))
            except IndexError:
                break
            accepting, syms = nfa.send(oursym)
            oursyms += oursym
        return accepting, syms, oursyms


    async def dispatch(self,text):
        await self.inq.put(text)

    async def askPersonality(self):
        text = Personality.text(self.personality)
        buttons = [[{'text':text,'callback_data':text} for text in ['shy','chatty','hyper']]]
        await self.telegram.sendMessage(self.chat_id,text,{'inline_keyboard':buttons})

    async def reply(self,text,their_choices=None):
        if their_choices:
            options = {'keyboard':[list(their_choices)],'resize_keyboard':True}
        else:
            options = {}
        await self.telegram.sendMessage(self.chat_id,text,options)

class Personality:
    Shy = object()
    Chatty = object()
    Hyper = object() # Bossy/Pushy?

    @staticmethod
    def of(text):
        return {
            'shy': Personality.Shy,
            'chatty': Personality.Chatty,
            'hyper': Personality.Hyper,
        }[text]

    @staticmethod
    def text(personality):
        return {
            Personality.Shy: 'shy',
            Personality.Chatty: 'chatty',
            Personality.Hyper: 'hyper'
        }[personality]

def nreplies(personality):
    return {
        Personality.Shy: 0,
        Personality.Chatty: 1,
        Personality.Hyper: 99
    }[personality]

def parse(text):
    if text.startswith('/'):
        hd, *tl = text.split()
        return hd[1:],tl
    return None,text

log = logging.getLogger(__name__)