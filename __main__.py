import requests
import time
import json

CAPSOLVER_API_KEY = "CAP-F5238D35CBD407280A722AEC24E62FB22B065F6412A88E3A1E4A254AD7049B36"

PAGE_URL = "https://pt.namemc.com/minecraft-names?offset=3196800&sort=desc"
WEBSITE_KEY = "0x4AAAAAAADnOjc0PNeA8qVm"


def create_task():
    """
    Cria a tarefa de resolução de captcha na API do Capsolver.
    """
    print("Criando a tarefa...")
    payload = {
        "clientKey": CAPSOLVER_API_KEY,
        "task": {
            "type": "AntiCloudflareTaskProxyLess",
            "websiteURL": PAGE_URL,
            "websiteKey": WEBSITE_KEY,
        }
    }

    try:
        response = requests.post("https://api.capsolver.com/createTask", json=payload)
        response.raise_for_status()

        resp_json = response.json()
        if resp_json.get("errorId") != 0:
            print(f"Erro ao criar a tarefa: {resp_json.get('errorDescription')}")
            return None

        print(f"Tarefa criada com sucesso. ID da Tarefa: {resp_json.get('taskId')}")
        return resp_json.get("taskId")

    except requests.RequestException as e:
        print(f"Erro de conexão: {e}")
        return None


def get_solution(task_id):
    """
    Consulta a API para obter a solução do captcha.
    """
    if not task_id:
        return None

    print("Aguardando a solução...")
    payload = {
        "clientKey": CAPSOLVER_API_KEY,
        "taskId": task_id
    }

    while True:
        try:
            response = requests.post("https://api.capsolver.com/getTaskResult", json=payload)
            response.raise_for_status()

            resp_json = response.json()
            status = resp_json.get("status", "")

            if status == "ready":
                print("Solução recebida!")
                return resp_json.get("solution")

            if status == "failed" or resp_json.get("errorId") != 0:
                print(f"Falha na resolução: {resp_json.get('errorDescription')}")
                return None

            # Aguarda antes de verificar novamente
            time.sleep(2)

        except requests.RequestException as e:
            print(f"Erro de conexão ao obter o resultado: {e}")
            time.sleep(2)


def main():
    """
    Função principal que orquestra a criação e obtenção da solução.
    """
    task_id = create_task()
    solution = get_solution(task_id)

    if solution:
        print("\n--- Solução do Captcha ---")
        print(solution)


if __name__ == "__main__":
    main()
