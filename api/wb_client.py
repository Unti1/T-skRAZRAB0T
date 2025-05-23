import json
from urllib import response
from aiohttp import ClientSession


class HTTPClient:
    def __init__(self, base_url: str):
        self._session = ClientSession(base_url=base_url)

    async def __aenter__(self):
        self._session = ClientSession(base_url=self._base_url)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._session.close()


class WBCardClient(HTTPClient):
    def __init__(self, base_url="https://card.wb.ru"):
        super().__init__(base_url=base_url)

    async def get_product_data(self, product_id: int | str):
        params = {
            "appType": 1,
            "curr": "rub",
            "dest": -2228364,
            "spp": 30,
            "hide_dtype": 10,
            "ab_testing": "false",
            "nm": int(product_id),
        }
        async with self._session.get("/cards/v2/detail", params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
            else:
                return resp.json()

        return data

    async def get_detail_per_product(self, product_id: int | str):
        params = {}
        async with self._session.get("/cards/v2/detail", params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data
            else:
                return await resp.json()

    async def take_details(self, product_id: str):
        product_id = str(product_id)

        async with ClientSession() as session:
            for id in range(10, 26):
                base_url = f"https://basket-{id}.wbbasket.ru"
                url = f"{base_url}/vol{product_id[:4]}/part{product_id[:6]}/{product_id}/info/ru/card.json"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        break

        return " | ".join(
            [
                data["imt_name"],
                data["slug"],
                data["subj_name"],
                data["subj_root_name"],
                data["description"],
            ]
        )


class WBSearchClient(HTTPClient):
    def __init__(self, base_url="https://search.wb.ru"):
        super().__init__(base_url=base_url)

    async def get_products_per_query(self, query: str):
        params = {
            "ab_testing": "false",
            "appType": "1",
            "curr": "rub",
            "dest": "-1116963",
            "hide_dtype": "13",
            "lang": "ru",
            "page": "1",
            "query": query,
            "resultset": "catalog",
            "sort": "popular",
        }
        async with self._session.get(
            "/exactmatch/ru/male/v13/search", params=params
        ) as resp:
            data = await resp.text()
            data = json.loads(data)
            return data
