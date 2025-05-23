import asyncio
import json
from api.wb_client import WBCardClient, WBSearchClient
from tools.keywords_extraction import extract_keywords_tfidf


async def test(product_id):
    wb_card_client = WBCardClient()
    wb_search_client = WBSearchClient()
    
    # data = await wb_card_client.get_product_data(product_id)
    description = await wb_card_client.take_details(product_id)
    keywords = extract_keywords_tfidf(description)
    search_request = ' '.join(keywords)
    print(f"Полученные ключевые слова: {keywords}\nПолученные из: {description}", )
    data = await wb_search_client.get_products_per_query(search_request)
    products = data["data"]["products"]
    with open('products.json', 'w', encoding='utf-8') as fl:
        json.dump(products, fl, indent=4, ensure_ascii=False)

    
    
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test(359063793))