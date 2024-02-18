import requests


def invoke(url: str, params_json: any):
    response = requests.post(url, json=params_json, headers={"Content-Type": f"application/json"})
    if response.ok:
        return response.json()["runId"]
    else:
        print(response.text)
        raise Exception(
            f"Error invoking logic app url at {url}. \n Status_Code: {response.status_code}. Text: {response.text}")
