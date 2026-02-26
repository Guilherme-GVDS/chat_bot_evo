from fastapi import FastAPI, Request
from bot.evolution_api import send_message

from bot.chains import get_conversational_rag_chain
app = FastAPI()

conversational_rag_chain = get_conversational_rag_chain()


@app.post('/webhook')
async def webhook(request: Request):
    data = await request.json()
    chat_id = data.get('data').get('key').get('remoteJid')
    message = data.get('data').get('message').get('conversation')

    if chat_id and message and '@g.us' not in chat_id:
        ai_response = conversational_rag_chain.invoke(
            input={'input': message},
            config={'configurable': {'session_id': chat_id}}
        )['answer']

        send_message(
            number=chat_id,
            text=ai_response
        )

    return {'status': 'ok'}
