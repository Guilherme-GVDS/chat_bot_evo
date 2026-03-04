import asyncio
from collections import defaultdict

import redis.asyncio

from bot.chains import get_conversational_rag_chain
from bot.evolution_api import evolution_client
from core.config import (
    BUFFER_KEY_SUFIX,
    BUFFER_TTL_SECONDS,
    DEBOUNCE_TIME_SECONDS,
    REDIS_URL,
)

redis_client = redis.asyncio.from_url(REDIS_URL, decode_responses=True)
conversarional_rag_chain = get_conversational_rag_chain()
debounce_tasks = defaultdict(asyncio.Task)


def log(*args):
    print("[MessageBuffer]", *args)


async def buffer_message(chat_id, message):
    buffer_key = f"{chat_id}{BUFFER_KEY_SUFIX}"
    await redis_client.rpush(buffer_key, message)
    await redis_client.expire(buffer_key, BUFFER_TTL_SECONDS)

    log(f"Mensagem adicionada ao buffer de {chat_id}: {message}")

    if debounce_tasks.get(chat_id):
        debounce_tasks[chat_id].cancel()
        log(f"Debounce resetado para {chat_id}")

    debounce_tasks[chat_id] = asyncio.create_task(handle_debounce(chat_id))


async def handle_debounce(chat_id):
    try:
        log(f'Iniciando debounce para {chat_id}')
        await asyncio.sleep(float(DEBOUNCE_TIME_SECONDS))
        buffer_key = f"{chat_id}{BUFFER_KEY_SUFIX}"
        messages = await redis_client.lrange(buffer_key, 0, -1)
        full_message = " ".join(messages)

        if messages:

            log(f'Processando mensagem combinada para {chat_id}: {full_message}')

            ai_response = await conversarional_rag_chain.ainvoke(
                input={'input': full_message},
                config={'configurable': {'session_id': chat_id}},
            )['answer']

            await evolution_client.send_message(chat_id, ai_response)
        await redis_client.delete(buffer_key)
    except asyncio.CancelledError:
        log(f'Debounce cancelado para {chat_id}')
