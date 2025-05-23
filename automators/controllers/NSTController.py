import json
import urllib.parse
from settings.config import settings

async def launch_and_return_browser_ws_endpoint(profile_id, headless=False):
    host = 'localhost:8848'
    api_key = settings['NST_Token']
    config = {
        "headless": headless,
        "autoClose": True
    }
    
    query = urllib.parse.urlencode({
        'x-api-key': api_key,
        'config': json.dumps(config)
    })
    browser_ws_endpoint = f"ws://{host}/devtool/launch/{profile_id}?{query}"
    print('browserWSEndpoint:', browser_ws_endpoint)
    return browser_ws_endpoint