import logging
import asyncio
import traceback

class Task:
    def __init__(self):
        self.id = id(self)
        self.result = asyncio.Future()
        self.task = None
        self.children = []

    def start(self,*args,**kwargs):
        self.task = asyncio.ensure_future(self._clean_run(*args,**kwargs))
        return self.task

    def spawn(self,child):
        self.children.append(child)
        child.start()
        return child

    async def children_done(self):
        if self.children:
            try:
                await asyncio.wait([await child.result for child in self.children])
            except:
                log.debug('{}: Child stopped with exception.'.format(self.id))

    async def stop_children(self):
        waitfor = []
        for child in self.children:
            if not child.task.done(): #and not task is asyncio.Task.current_task():
                waitfor.append(child.stop())
        if waitfor:
            await asyncio.wait(waitfor) # necessary for server close

    async def stop(self):
        self.task.cancel()
        try:
            await self.result
            log.debug('Task {} finished with result {}.'.format(self.id,self.result.result()))
        except asyncio.CancelledError:
            log.debug('Task {} cancelled.'.format(self.id))


    async def _clean_run(self,*args,**kwargs):
        try:
            res = await self._run(*args,**kwargs)
            self.result.set_result(res)
        except Exception as e:
            if not isinstance(e,asyncio.CancelledError):
                log.error('Exception in task {}:\n{}'.format(self.id,traceback.format_exc()))
            self.result.set_exception(e)
        await self.stop_children()

    async def _run(self):
        raise NotImplementedError('abstract!')

log = logging.getLogger(__name__)