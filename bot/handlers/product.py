from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import LinkPreviewOptions, Message

from api.wb_client import WBCardClient, WBSearchClient
from tools.keywords_extraction import extract_keywords_tfidf


r = Router()


async def get_pos_in_search(
    product_id: int, keywords: list[str], wb_search_client: WBSearchClient
) -> dict:
    product_pos = {}
    for search_keyword in keywords:
        position = 0
        found = False
        data = await wb_search_client.get_products_per_query(search_keyword)
        if data['data']['total'] < 5000:
            for page in range(1, data['data']['total']//100 + 1):  
                data = await wb_search_client.get_products_per_query(search_keyword, page =page)
                products = data["data"]["products"]
                for product in products:
                    position += 1
                    if product["id"] == product_id:
                        product_pos[search_keyword] = position
                        found = True
                        break
                if found:
                    break
        if not found:
            product_pos[search_keyword] = "Не найдена"
            
    return product_pos


@r.message(Command("start"))
async def start_message(message: Message):
    await message.answer(
        "Приветствую! Для того чтобы получить позицию товара по ключевому слову в запросе, отправьте ссылку на ваш товар из WB. Ссылка должна быть в формате https://www.wildberries.ru/catalog/XXXXXXXX/..."
    )


@r.message(F.text)
async def analyze_product_url(
    message: Message, wb_card: WBCardClient, wb_search: WBSearchClient
):
    url = message.text
    er_message = "Неверный формат ссылки! Пример корректной ссылки: `https://www.wildberries.ru/catalog/XXXXXXXX/detail.aspx?...`"

    if "wildberries" not in url:
        await message.answer(er_message)
        return

    url_parts: list[str] = message.text.split("/")
    if not url_parts[4].isdigit():
        await message.answer(er_message)
        return

    product_id = int(url_parts[4])

    description = await wb_card.take_details(product_id)
    keywords = extract_keywords_tfidf(description)
    await message.answer(
        f"Полученные ключевые слова по продукту из ссылки {url} -> {keywords}",
    )
    products_position_for_keywords = await get_pos_in_search(
        product_id,
        keywords,
        wb_search
        
    )
    await message.answer(
        f"Какие позиции занимает ваш продукт в поиске:\n"
        + "\n".join(
            [
                f"По запросу: \"{query}\" => {value} позиция в поиске"
                for query, value in products_position_for_keywords.items()
            ]
        ),
    )
