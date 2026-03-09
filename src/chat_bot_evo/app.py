from fastapi import FastAPI, Request
from datetime import datetime, timezone
from bot.message_buffer import buffer_message

app = FastAPI()


@app.post('/webhook')
async def webhook(request: Request):
    data = await request.json()
    data_block = data.get('data') or {}

    # Ignora mensagens antigas para evitar reprocessamento durante o
    # sync do WhatsApp ao reconectar após queda do container
    message_timestamp = data_block.get('messageTimestamp')
    if message_timestamp:
        message_time = datetime.fromtimestamp(int(message_timestamp),
                                              tz=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        age_minutes = (now - message_time).total_seconds() / 60
        if age_minutes > 5:
            return {'status': 'ignored'}

    chat_id = (data_block.get('key') or {}).get('remoteJid')
    message = (data_block.get('message') or {}).get('conversation')

    # Filtra mensagens de grupos (@g.us)
    # o bot responde apenas em chats privados
    if chat_id and message and '@g.us' not in chat_id:
        await buffer_message(chat_id, message)

    return {'status': 'ok'}
