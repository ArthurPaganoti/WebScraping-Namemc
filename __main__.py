import requests
import time

CAPSOLVER_API_KEY = "CAP-F5238D35CBD407280A722AEC24E62FB22B065F6412A88E3A1E4A254AD7049B36"

PAGE_URL = "https://pt.namemc.com/minecraft-names?offset=3196800&sort=desc"
WEBSITE_KEY = "0x4AAAAAAADnOjc0PNeA8qVm"


def capsolver():
    payload = {
        "clientKey": CAPSOLVER_API_KEY,
        "task": {
            "type": 'AntiTurnstileTaskProxyLess',
            "websiteKey": WEBSITE_KEY,
            "websiteURL": PAGE_URL,
            "metadata": {
                "action": ""
            }
        }
    }
    res = requests.post("https://api.capsolver.com/createTask", json=payload)
    resp = res.json()
    task_id = resp.get("taskId")
    if not task_id:
        print("Falha ao criar a tarefa:", res.text)
        return
    print(f"Tarefa criada com sucesso. ID da Tarefa: {task_id} / Aguardando resultado...")

    while True:
        time.sleep(1)  # atraso
        payload = {"clientKey": CAPSOLVER_API_KEY, "taskId": task_id}
        res = requests.post("https://api.capsolver.com/getTaskResult", json=payload)
        resp = res.json()
        status = resp.get("status")
        if status == "ready":
            return resp.get("solution", {}).get('token')
        if status == "failed" or resp.get("errorId"):
            print("Falha na resolução! Resposta:", res.text)
            return


def main():
    """
    Função principal que orquestra a criação e obtenção da solução.
    """
    token = capsolver()
    print(token)


if __name__ == "__main__":
    main()
