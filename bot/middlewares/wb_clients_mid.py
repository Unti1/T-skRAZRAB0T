

from aiogram import BaseMiddleware

from api.wb_client import WBCardClient, WBSearchClient


class WBClientsMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.wb_card = WBCardClient()
        self.wb_search = WBSearchClient()
        
    async def __call__(self, handler, event, data):
        data["wb_card"] = self.wb_card
        data["wb_search"] = self.wb_search
        return await handler(event, data)