import asyncio
import requests
import json
import random
from urllib.parse import urlparse
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup

START_URL = "https://pt.namemc.com/minecraft-names?offset=3196800&sort=desc"
USER_DATA_DIR = "./my_browser_session"


def get_proxy_config() -> dict:
    random_port = random.randint(10001, 10100)
    proxy_uri = f"http://spkt1yrhhb:kf54FKIoeImfigz3+0@dc.decodo.com:{random_port}"
    parsed_uri = urlparse(proxy_uri)
    proxy_config = {
        "server": f"{parsed_uri.scheme}://{parsed_uri.hostname}:{parsed_uri.port}",
        "username": parsed_uri.username,
        "password": parsed_uri.password,
    }
    print(f"Usando proxy: {proxy_config['server']}")
    return proxy_config


async def get_verified_session(url: str) -> dict | None:
    print("Iniciando navegador com proxy...")
    proxy_settings = get_proxy_config()

    try:
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=False,
                args=["--start-maximized"],
                no_viewport=True,
                proxy=proxy_settings
            )
            page = await context.new_page()
            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            await page.goto(url, timeout=120000)

            print("Aguardando solução do desafio Cloudflare...")
            await page.wait_for_selector('//a[starts-with(@href, "/profile/")]', timeout=120000)
            print("Sessão verificada com sucesso.")

            cookies = await context.cookies()
            user_agent = await page.evaluate("() => navigator.userAgent")
            await context.close()
            return {"cookies": cookies, "user_agent": user_agent}

    except PlaywrightTimeoutError:
        print("Erro: Tempo limite atingido ao verificar a sessão. O proxy ou o site podem estar com problemas.")
        return None
    except Exception as e:
        print(f"Erro inesperado no Playwright: {e}")
        return None


def scrape_and_get_data(session_data: dict, url: str) -> list | None:
    if not session_data:
        print("Erro: Sessão inválida, extração de dados cancelada.")
        return None

    print("Iniciando extração de dados...")
    s = requests.Session()
    for cookie in session_data['cookies']:
        s.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
    s.headers.update({"User-Agent": session_data['user_agent']})

    try:
        response = s.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        scraped_data = []
        table_rows = soup.select('div.card-body > table > tbody > tr')

        for row in table_rows:
            cols = row.find_all('td')
            if len(cols) >= 2:
                name = cols[0].text.strip()
                drop_time = cols[1].text.strip()
                scraped_data.append({"name": name, "drop_time": drop_time})
        return scraped_data

    except requests.RequestException as e:
        print(f"Erro ao extrair dados: {e}")
        return None


async def main():
    session_data = await get_verified_session(START_URL)
    if session_data:
        scraped_data = scrape_and_get_data(session_data, START_URL)
        if scraped_data:
            output_filename = 'minecraft_names.json'
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(scraped_data, f, ensure_ascii=False, indent=4)
            print(f"\nOperação concluída: {len(scraped_data)} nomes salvos em '{output_filename}'.")


if __name__ == "__main__":
    asyncio.run(main())