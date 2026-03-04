import httpx


from core.config import (
    EVOLUTION_API_URL,
    EVOLUTION_AUTHENTICATION_API_KEY,
    EVOLUTION_INSTANCE_NAME,
)


class EvolutionAPI:

    def __init__(self):
        self.__api_url = EVOLUTION_API_URL
        self.__headers = {
            'apikey': EVOLUTION_AUTHENTICATION_API_KEY,
            'Content-Type': 'application/json',
        }
        self.__instance_name = EVOLUTION_INSTANCE_NAME
        self.__client = httpx.AsyncClient(timeout=10.0)

    async def send_message(self, chat_id: str, message: str) -> dict:
        url = f'{self.__api_url}/message/sendText/{self.__instance_name}'
        payload = {'number': chat_id, 'text': message}
        response = await self.__client.post(
            url,
            json=payload,
            headers=self.__headers,
        )
        response.raise_for_status()
        return response.json()


evolution_client = EvolutionAPI()
