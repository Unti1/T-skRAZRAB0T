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
    print(f"Полученные ключевые слова: {keywords}\nПолученные из: {description}", )
    product_pos = {}
    for search_keyword in keywords:
        position = 0
        found = False
        data = await wb_search_client.get_products_per_query(search_keyword)
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
            
    print(product_pos)
    with open('products.json', 'w', encoding='utf-8') as fl:
        json.dump(data, fl, indent=4, ensure_ascii=False)

    
    
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test(359063793))