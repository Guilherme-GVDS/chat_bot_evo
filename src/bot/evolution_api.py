import requests

from core.config import (
    EVOLUTION_API_URL,
    EVOLUTION_AUTHENTICATION_API_KEY,
    EVOLUTION_INSTANCE_NAME,
)


def send_message(number, text):
    url = f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE_NAME}"
    headers = {
        "apikey": EVOLUTION_AUTHENTICATION_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {"number": number, "text": text}
    requests.post(url=url, json=payload, headers=headers)
