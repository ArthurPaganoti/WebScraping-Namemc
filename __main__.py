import requests
import time
import random
import json

api_key = "CAP-F5238D35CBD407280A722AEC24E62FB22B065F6412A88E3A1E4A254AD7049B36"
site_key = "0x4AAAAAAADnOjc0PNeA8qVm"
site_url = "https://pt.namemc.com/minecraft-names?offset=3196800&sort=desc"


def capsolver():
    payload = {
        "clientKey": api_key,
        "task": {
            "type": 'AntiTurnstileTaskProxyLess',
            "websiteKey": site_key,
            "websiteURL": site_url,
            "metadata": {
                "action": ""  # optional
            }
        }
    }
    res = requests.post("https://api.capsolver.com/createTask", json=payload)
    resp = res.json()
    task_id = resp.get("taskId")
    if not task_id:
        print("Failed to create task:", res.text)
        return
    print(f"Got taskId: {task_id} / Getting result...")

    while True:
        time.sleep(1)  # delay
        payload = {"clientKey": api_key, "taskId": task_id}
        res = requests.post("https://api.capsolver.com/getTaskResult", json=payload)
        resp = res.json()
        status = resp.get("status")
        if status == "ready":
            return resp.get("solution", {}).get('token')
        if status == "failed" or resp.get("errorId"):
            print("Solve failed! response:", res.text)
            return


def get_random_proxy_uri():
    """
    Retorna uma URI de proxy aleatória.
    """
    random_number = random.randint(10001, 10100)
    return f"http://spkt1yrhhb:kf54FKIoeImfigz3+0@dc.decodo.com:{random_number}"


def get_and_save_page(url, filename):
    """
    Faz uma requisição GET usando proxy e salva o conteúdo em um arquivo JSON.
    """
    proxies = {
        'http': get_random_proxy_uri(),
        'https': get_random_proxy_uri(),
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Accept-Language': 'pt-BR,pt;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    try:
        response = requests.get(url, proxies=proxies, headers=headers, timeout=10)
        response.raise_for_status()
        data = {'url': url, 'content': response.text}
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Página salva em {filename}")
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar {url}: {e}\nResposta: {getattr(e.response, 'text', None)}")


def main():
    token = capsolver()
    print(token)
    url = site_url
    filename = 'pagina.json'
    get_and_save_page(url, filename)


if __name__ == "__main__":
    main()
