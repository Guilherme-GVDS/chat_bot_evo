from fastapi import FastAPI, Request
from .evolution_api import send_message

app = FastAPI()


@app.post('/webhook')
async def webhook(request: Request):
    data = await request.json()
    chat_id = data.get('data').get('key').get('remoteJid')
    message = data.get('data').get('message').get('conversation')

    if chat_id and message and '@g.us' not in chat_id:
        print(f'deveria enviar mensagem para {chat_id}')
        send_message(
            number=chat_id,
            text=f'Você enviou {message} para mim?'
        )
    print(f'data: {data}')
    return {'status': 'ok'}
