from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import LinkPreviewOptions, Message

from api.wb_client import WBCardClient, WBSearchClient
from tools.keywords_extraction import extract_keywords_tfidf


r = Router()


def get_top_10_items(searched_data: list[dict]):
    result = ""
    for i, product in enumerate(searched_data):
        if i > 9:
            break
        result += (
            f"[ #{i+1} ] Название: {product['name']}\n Цена: {product['sizes'][0]['price']['total']/100} ₽\nСсылка: https://www.wildberries.ru/catalog/{product['id']}/detail.aspx"
        )
        result += "\n\n"
    return result


@r.message(Command("start"))
async def start_message(message: Message):
    await message.answer(
        "Приветствую! Для того чтобы получить топ 10 товаров аналогичных вашему, отправьте ссылку на ваш товар из WB. Ссылка должна быть в формате https://www.wildberries.ru/catalog/XXXXXXXX/..."
    )


@r.message(F.text)
async def get_product_url(
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

    product_id = url_parts[4]

    description = await wb_card.take_details(product_id)
    keywords = extract_keywords_tfidf(description)
    search_request = " ".join(keywords)
    await message.answer(
        f"Полученные ключевые слова по продукту из ссылки {url} -> {keywords}",
    )
    searched_data = await wb_search.get_products_per_query(search_request)
    summary_products = get_top_10_items(searched_data["data"]["products"])
    await message.answer(
        f"Вот что мне удалось найти аналогично вашему товару...\n{summary_products}",
        link_preview_options=LinkPreviewOptions(is_disabled=True)
    )
