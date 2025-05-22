import psutil
import json
import random
import requests
from settings import *

platforms_array = ["macos", "windows", "linux"]

vendors_array = ["Google Inc. (Intel)", "Google Inc. (NVIDIA)", "Google Inc. (AMD)", "Google Inc.",
                 "Google Inc. (Microsoft)", "Google Inc. (Unknown)", "Intel Inc.",
                 "Google Inc. (NVIDIA Corporation)"]

renderers_array = {"Google Inc. (Intel)": [
    "ANGLE (Intel, Intel(R) HD Graphics Family Direct3D11 vs_5_0 ps_5_0, D3D11)",
    "ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)"
],
    "Google Inc. (NVIDIA)": [
    "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 6GB Direct3D11 vs_5_0 ps_5_0, D3D11-30.0.14.7247)",
    "ANGLE (NVIDIA, NVIDIA GeForce GTX 1050 Ti Direct3D11 vs_5_0 ps_5_0, D3D11-27.21.14.6172)"
],
    "Google Inc. (AMD)": [
    "ANGLE (AMD, AMD Radeon(TM) Vega 10 Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)",
    "ANGLE (AMD, AMD Radeon(TM) Graphics Direct3D11 vs_5_0 ps_5_0, D3D11-30.0.13044.0)"
],
    "Google Inc.": [
    "ANGLE (Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0)",
    "ANGLE (Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0)"
],
    "Google Inc. (Microsoft)": [
    "ANGLE (Microsoft, Microsoft Basic Render Driver Direct3D11 vs_5_0 ps_5_0, D3D11-10.0.19041.546)",
    "ANGLE (Microsoft, Microsoft Basic Render Driver Direct3D11 vs_5_0 ps_5_0, D3D11-6.3.9600.16505)"
],
    "Google Inc. (Unknown)": [
    "ANGLE (Unknown, Qualcomm(R) Adreno(TM) 630 GPU Direct3D11 vs_5_0 ps_5_0, D3D11)",
    "ANGLE (Unknown, Qualcomm(R) Adreno(TM) 630 GPU Direct3D11 vs_5_0 ps_5_0, D3D11-25.18.10500.0)"
],
    "Intel Inc.": [
    "Intel Iris OpenGL Engine"
],
    "Google Inc. (NVIDIA Corporation)": [
    "ANGLE (NVIDIA Corporation, GeForce RTX 3070/PCIe/SSE2, OpenGL 4.5.0 NVIDIA 461.40)"
]}
cpu = [2, 4, 6, 8, 12, 16]
memory = [2, 4, 8]


def authentication(username: str = '', password: str = ''):
    return config["Dolphin"]["token"]


def get_new_user_agent(platform: str, session: requests.Session):
    version_number = random.randint(101, 107)
    options = {
        "url": f"https://anty-api.com/fingerprints/useragent?browser_type=anty&browser_version=107&" +
               f"platform={platform}"
    }
    response = session.get(options["url"]).json()
    # print(response)
    if "data" in response:
        return response["data"]
    else:
        raise Exception("Can't get new user agent, something went wrong")


def create_profile_and_send_id(session: requests.Session):
    null = None

    # set current parameters for browser profile
    current_vendor = random.choice(vendors_array)
    current_renderer = random.choice(renderers_array[current_vendor])
    current_platform = random.choice(platforms_array)

    current_user_agent = get_new_user_agent(
        platform=current_platform, session=session)
    
    # set options for browser profile
    options = {
        "url": "https://anty-api.com/browser_profiles",
        "data": {
            "platform": current_platform,
            "browserType": "anty",
            "useragent": {
                "mode": "manual",
                "value": current_user_agent
            },
            "webrtc": {
                "mode": "altered",
                "ipAddress": null
            },
            "canvas": {
                "mode": "real"
            },
            "webgl": {
                "mode": "real"
            },
            "webglInfo": {
                "mode": "manual",
                "vendor": current_vendor,
                "renderer": current_renderer
            },
            "geolocation": {
                "mode": "real",
                "latitude": null,
                "longitude": null
            },
            "cpu": {
                "mode": "manual",
                "value": random.choice(cpu)
            },
            "memory": {
                "mode": "manual",
                "value": random.choice(memory)
            },
            "timezone": {
                "mode": "auto",
                "value": null
            },
            "locale": {
                "mode": "auto",
                "value": null
            },
            "name": "Current Bot",
            "tags": [
                ""
            ],
            "mainWebsite": "",
            "notes": {
                "content": null,
                "color": "blue",
                "style": "text",
                "icon": null
            },
            "proxy": null,
            "statusId": 0,
            "doNotTrack": False
        }
    }
    response = session.post(options["url"], data=json.dumps(options["data"]))
    # print(response.json())
    profile_id = get_last_browser_profile(session=session)
    session.close()
    return profile_id['id']


def get_last_browser_profile(session: requests.Session):
    options = {
        "url": "https://anty-api.com/browser_profiles"
    }
    response = session.get(options["url"]).json()
    if "data" in response:
        return response["data"][0]
    else:
        raise Exception("Can't get list of browser profiles")


def delete_browser_profile(session: requests.Session, profile_id: str):
    options = {
        'url': "https://anty-api.com/browser_profiles/"
    }
    response = session.delete(options["url"] + str(profile_id))
    # print(response.json())

def get_profile_data(session, profile_id: str,):
    options = {
        "url": f"https://dolphin-anty-api.com/browser_profiles/{profile_id}"
        # "url": f"http://localhost:3001/v1.0/browser_profiles/{profile_id}"
    }
    response = session.get(options['url']).json()
    return response

def start_automation(session, profile_id: str, headless: bool = False):
    headless_param = '&headless=1' if headless else ''
    nosand_param = '&no-sendbox'
    options = {
        "url": f"http://localhost:3001/v1.0/browser_profiles/{profile_id}/start?automation=1{headless_param}"
    }
    response = session.get(options['url']).json()
    return response

def stop_automation(session, profile_id: str):

    options = {
        "url": f"http://localhost:3001/v1.0/browser_profiles/{profile_id}/stop"
    }
    response = session.get(options['url']).json()
    #TODO: Тут должно быть ожидание пока закроется браузер
    return response

