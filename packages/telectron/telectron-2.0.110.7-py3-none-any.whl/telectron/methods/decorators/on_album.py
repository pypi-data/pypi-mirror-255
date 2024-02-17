import asyncio
from typing import Callable
import inspect
import functools

import telectron
from telectron.filters import Filter, album_message as album_message_filter


START_ALBUM_HACK_DELAY = 2
MAX_ALBUM_MESSAGES = 10
MIN_ALBUM_MESSAGES = 2


class OnAlbum:
    def on_album(
            self=None,
            filters=None,
            group: int = 0
    ) -> callable:

        def decorator(func: Callable) -> Callable:
            messages_filters = (self
                                if isinstance(self, Filter)
                                else filters)
            on_message_filters = (album_message_filter & messages_filters
                                  if messages_filters
                                  else album_message_filter)

            func = album_saver(func)

            if isinstance(self, telectron.Client):
                self.add_handler(telectron.handlers.MessageHandler(func, on_message_filters), group)
            elif isinstance(self, Filter) or self is None:
                if not hasattr(func, "handlers"):
                    func.handlers = []

                func.handlers.append(
                    (telectron.handlers.MessageHandler(func, on_message_filters), group)
                )

            return func

        return decorator


def album_saver(original_handler):
    async def wrapper(client: OnAlbum, message):
        async with client.album_lock:
            if message.media_group_id not in client.albums:
                client.albums[message.media_group_id] = AlbumChecker(client, message.media_group_id, original_handler)
                await client.albums[message.media_group_id].start_checking()
            album = client.albums[message.media_group_id]
        await album.add_message(message)
    return wrapper


class AlbumChecker:
    def __init__(self, telegram_client, media_group_id, original_handler):
        self.telegram_client = telegram_client
        self.media_group_id = media_group_id
        self.original_handler = original_handler
        self.lock = asyncio.Lock()
        self.messages = []
        self.message_ids = set()
        self.expire_time = None
        self.delay = START_ALBUM_HACK_DELAY

    def get_current_time(self) -> float:
        return self.telegram_client.loop.time()

    async def add_message(self, message):
        async with self.lock:
            if message.id not in self.message_ids:
                self.messages.append(message)
                self.message_ids.add(message.id)
            if len(self.messages) < MAX_ALBUM_MESSAGES:
                self.expire_time = self.get_current_time() + self.delay

    async def start_checking(self):
        self.telegram_client.loop.create_task(self.check())

    async def check(self):
        while True:
            diff = self.expire_time - self.get_current_time()
            if diff <= 0 or len(self.messages) >= MAX_ALBUM_MESSAGES:
                if len(self.messages) < MIN_ALBUM_MESSAGES:
                    self.delay *= 2
                    self.expire_time = self.get_current_time() + self.delay
                    continue
                async with self.telegram_client.album_lock:
                    del self.telegram_client.albums[self.media_group_id]
                    self.telegram_client.loop.create_task(self.run_handler())
                return

            await asyncio.sleep(diff)

    async def run_handler(self):
        self.messages.sort(key=lambda m: m.id)
        func = functools.partial(self.original_handler, self.telegram_client, self.messages)
        if inspect.iscoroutinefunction(self.original_handler):
            await func()
        else:
            await self.telegram_client.loop.run_in_executor(self.telegram_client.executor, func)
