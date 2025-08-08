import requests
import time
import json
import random
from bs4 import BeautifulSoup

API_KEY = "CAP-F5238D35CBD407280A722AEC24E62FB22B065F6412A88E3A1E4A254AD7049B36"
SITE_URL = "https://pt.namemc.com/minecraft-names?offset=3196800&sort=desc"
SITE_KEY = "0x4AAAAAAADnOjc0PNeA8qVm"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
}

def get_random_proxy_uri():
    """
    Retorna uma URI de proxy aleatória.
    """
    random_number = random.randint(10001, 10100)
    return f"http://spkt1yrhhb:kf54FKIoeImfigz3+0@dc.decodo.com:{random_number}"

def get_turnstile_token(api_key, site_key, site_url, proxy_uri=None):
    payload = {
        "clientKey": api_key,
        "task": {
            "type": "AntiTurnstileTaskProxyLess",
            "websiteKey": site_key,
            "websiteURL": site_url
        }
    }
    proxies = {"http": proxy_uri, "https": proxy_uri} if proxy_uri else None
    res = requests.post("https://api.capsolver.com/createTask", json=payload, proxies=proxies)
    task_id = res.json().get("taskId")
    if not task_id:
        print("Erro ao criar task:", res.text)
        return None
    while True:
        time.sleep(2)
        res = requests.post("https://api.capsolver.com/getTaskResult", json={
            "clientKey": api_key,
            "taskId": task_id
        }, proxies=proxies)
        data = res.json()
        if data.get("status") == "ready":
            return data["solution"]["token"]
        if data.get("status") == "failed" or data.get("errorId"):
            print("Falha ao resolver captcha:", res.text)
            return None

def get_namemc_page(token):
    url = SITE_URL
    headers = HEADERS.copy()
    headers['cf-turnstile-response'] = token
    cookies = {'cf-turnstile-response': token}
    resp = requests.get(url, headers=headers, cookies=cookies)
    return resp.text

def extrair_nomes(html):
    soup = BeautifulSoup(html, "html.parser")
    nomes = []
    for a in soup.select('.card-body a'):
        nome = a.get_text(strip=True)
        if nome:
            nomes.append({"nome": nome})
    with open("namemc_nomes.json", "w", encoding="utf-8") as f:
        json.dump(nomes, f, ensure_ascii=False, indent=2)
    print(f"{len(nomes)} nomes salvos em namemc_nomes.json")

if __name__ == "__main__":
    print("Resolvendo captcha...")
    proxy_uri = get_random_proxy_uri()
    token = get_turnstile_token(API_KEY, SITE_KEY, SITE_URL, proxy_uri)
    if not token:
        print("Não foi possível resolver o captcha.")
        exit(1)
    print("Captcha resolvido, acessando página...")
    html = get_namemc_page(token)
    extrair_nomes(html)
