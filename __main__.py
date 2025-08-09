import asyncio
import requests
import json  # Importe o módulo JSON
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup

START_URL = "https://pt.namemc.com/minecraft-names?offset=3196800&sort=desc"
NEXT_PAGE_URL = "https://pt.namemc.com/minecraft-names?sort=desc&offset=25"
USER_DATA_DIR = "./my_browser_session"


async def get_verified_session(url: str) -> dict | None:

    print("🚀 Lançando o navegador com configurações stealth manuais...")
    try:
        async with async_playwright() as p:
            context = await p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=False,
                args=["--start-maximized"],
                no_viewport=True,
            )
            page = await context.new_page()
            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("Navegando para o site...")
            await page.goto(url, timeout=120000)
            print("⏳ Aguardando Cloudflare ou o conteúdo...")
            try:
                await page.wait_for_selector('//a[starts-with(@href, "/profile/")]', timeout=5000)
                print("✅ Conteúdo já presente. Nenhum desafio foi necessário.")
            except PlaywrightTimeoutError:
                print("Desafio detectado. Aguardando a resolução...")
                await page.wait_for_selector('//a[starts-with(@href, "/profile/")]', timeout=120000)
                print("✅ Desafio do Cloudflare resolvido!")
            cookies = await context.cookies()
            user_agent = await page.evaluate("() => navigator.userAgent")
            await context.close()
            return {"cookies": cookies, "user_agent": user_agent}
    except PlaywrightTimeoutError:
        print("❌ O tempo limite foi atingido. A proteção do site pode ser muito forte ou o IP está sinalizado.")
        return None
    except Exception as e:
        print(f"Um erro inesperado ocorreu: {e}")
        return None


# --- ATENÇÃO ÀS MUDANÇAS AQUI ---
def scrape_and_get_data(session_data: dict, url: str) -> list | None:

    if not session_data:
        print("Não é possível extrair dados, a sessão é inválida.")
        return None

    print(f"\n⚙️  Preparando para extrair dados de {url} com a sessão verificada...")
    s = requests.Session()
    for cookie in session_data['cookies']:
        s.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
    s.headers.update({"User-Agent": session_data['user_agent']})

    try:
        response = s.get(url)
        response.raise_for_status()
        print(f"✔️ Página buscada com sucesso, status: {response.status_code}")

        soup = BeautifulSoup(response.text, 'html.parser')

        scraped_data = []

        table_rows = soup.select('div.card-body > table > tbody > tr')

        for row in table_rows:
            cols = row.find_all('td')
            if len(cols) >= 2:
                name = cols[0].text.strip()
                drop_time = cols[1].text.strip()

                scraped_data.append({
                    "name": name,
                    "drop_time": drop_time
                })

        return scraped_data

    except requests.RequestException as e:
        print(f"❌ Falha ao extrair dados com a sessão: {e}")
        return None


async def main():

    session_data = await get_verified_session(START_URL)
    if session_data:
        scraped_data = scrape_and_get_data(session_data, START_URL)

        if scraped_data:
            output_filename = 'minecraft_names.json'

            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(scraped_data, f, ensure_ascii=False, indent=4)

            print(f"\n✨ Operação concluída! Foram salvos {len(scraped_data)} nomes no arquivo '{output_filename}'.")


if __name__ == "__main__":
    asyncio.run(main())