import asyncio

class FiniteQueue(asyncio.Queue):
    End = object()
    def __aiter__(self):
        return self
    async def close(self):
        await self.put(FiniteQueue.End) # how to dispatch this to all getters?
    async def __anext__(self):
        elt = await self.get()
        if elt is FiniteQueue.End:
            # maybe here? self.put_nowait(FiniteQueue.End)
            raise StopAsyncIteration
        else:
            return elt