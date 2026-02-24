FROM python:3.13

WORKDIR /app

COPY requirements.txt .
RUN apt update
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

EXPOSE 8000

CMD uvicorn chat_bot_evo.app:app --host 0.0.0.0 --port 8000

