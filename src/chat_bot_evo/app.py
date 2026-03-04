from fastapi import FastAPI, Request

from bot.message_buffer import buffer_message

app = FastAPI()


@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    data_block = data.get("data") or {}
    chat_id = (data_block.get("key") or {}).get("remoteJid")
    message = (data_block.get("message") or {}).get("conversation")

    if chat_id and message and "@g.us" not in chat_id:
        await buffer_message(chat_id, message)

    return {"status": "ok"}
