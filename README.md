# chat_bot_evo

Bot de atendimento via WhatsApp com RAG (Retrieval-Augmented Generation), construído com FastAPI, LangChain e Evolution API. O bot recebe mensagens, consulta uma base de conhecimento em documentos e responde com o contexto correto, mantendo histórico de conversa por sessão.

## Visão geral da arquitetura

```
WhatsApp → Evolution API → webhook → FastAPI (bot)
                                          ↓
                                   Message Buffer (Redis)
                                          ↓
                                   RAG Chain (LangChain)
                                          ↓
                                   LLM (Groq) + Vectorstore (Chroma)
                                          ↓
                                   Evolution API → WhatsApp
```

- **Evolution API** — conecta ao WhatsApp e encaminha mensagens via webhook
- **FastAPI** — recebe os webhooks e filtra mensagens válidas
- **Redis** — acumula mensagens em sequência (debounce) e armazena histórico de conversa por sessão
- **LangChain + Groq** — processa a mensagem com histórico e contexto dos documentos
- **Chroma** — vectorstore local para busca semântica nos documentos da base de conhecimento
- **HuggingFace** — modelo de embeddings para indexação dos documentos

> **Sobre os modelos:** o projeto utiliza **Groq** como provedor do LLM e **HuggingFace** para os embeddings, mas o LangChain suporta diversos outros provedores — como OpenAI, Anthropic, Ollama (local), entre outros. Para trocar, basta substituir as integrações em `chains.py` (LLM) e `vector_store.py` (embeddings) pelo pacote correspondente do LangChain, e ajustar as variáveis de ambiente no `.env`.

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/install/)
- Conta na [Groq](https://console.groq.com/) com uma API Key
- Conta na [HuggingFace](https://huggingface.co/) com uma API Key

## Instalação e execução local

### 1. Clone o repositório

```bash
git clone https://github.com/Guilherme-GVDS/chat_bot_evo.git
cd chat_bot_evo
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o `.env` e preencha os valores obrigatórios:

| Variável | Descrição |
|---|---|
| `GROQ_API_KEY` | Chave da API Groq |
| `GROQ_MODEL_NAME` | Modelo a usar (ex: `llama-3.3-70b-versatile`) |
| `GROQ_MODEL_TEMPERATURE` | Temperatura do modelo (ex: `0.7`) |
| `HUGGINGFACE_API_KEY` | Chave da API HuggingFace |
| `EVOLUTION_INSTANCE_NAME` | Nome da instância na Evolution API |
| `AUTHENTICATION_API_KEY` | Chave de autenticação da Evolution API |
| `POSTGRES_PASSWORD` | Senha do banco de dados PostgreSQL |

> As demais variáveis já possuem valores padrão funcionais no `.env.example`.

### 3. Adicione documentos à base de conhecimento (opcional)

Coloque arquivos `.txt` ou `.pdf` na pasta `data/rag_files/`. Eles serão indexados automaticamente na primeira inicialização do bot.

```bash
mkdir -p data/rag_files
cp meu_documento.pdf data/rag_files/
```

> Após a indexação, os arquivos são movidos automaticamente para `data/rag_files/processed/`.

### 4. Suba os containers

```bash
docker compose up -d
```

O Docker Compose sobe os seguintes serviços:
- **Evolution API** em `http://localhost:8080`
- **Bot (FastAPI)** em `http://localhost:8000`
- **PostgreSQL** em `localhost:5432`
- **Redis** em `localhost:6379`

### 5. Configure a instância no WhatsApp

Acesse o painel da Evolution API em `http://localhost:8080` e:

1. Crie uma instância com o nome definido em `EVOLUTION_INSTANCE_NAME`
2. Conecte ao WhatsApp escaneando o QR Code
3. Configure o webhook apontando para `http://bot:8000/webhook`

## Comportamento do bot

- **Responde apenas em chats privados** — mensagens de grupos são ignoradas
- **Debounce de mensagens** — mensagens enviadas em sequência são acumuladas e processadas juntas, evitando múltiplas respostas
- **Histórico por sessão** — cada número de WhatsApp tem seu histórico de conversa independente, armazenado no Redis
- **Filtro de mensagens antigas** — mensagens com mais de 5 minutos são ignoradas para evitar reprocessamento após reinício do container

## Estrutura do projeto

```
chat_bot_evo/
├── src/
│   ├── bot/
│   │   ├── chains.py           # Pipeline RAG com LangChain
│   │   ├── evolution_api.py    # Cliente da Evolution API
│   │   ├── memory.py           # Histórico de conversa no Redis
│   │   ├── message_buffer.py   # Buffer e debounce de mensagens
│   │   └── prompts.py          # Templates de prompt
│   ├── chat_bot_evo/
│   │   └── app.py              # Webhook FastAPI (entrypoint)
│   ├── core/
│   │   └── config.py           # Variáveis de ambiente
│   └── rag/
│       └── vector_store.py     # Indexação e busca nos documentos
├── data/
│   ├── rag_files/              # Documentos para indexação (.txt, .pdf)
│   └── vectorstore/            # Índice Chroma persistido
├── .env.example
├── .gitignore
├── .dockerignore
├── docker-compose.yml
├── docker-compose.override.yml # Portas expostas para desenvolvimento local
├── Dockerfile
├── requirements.in             # Dependências diretas
└── requirements.txt            # Dependências completas (geradas via pip freeze)
```

## Comandos úteis

```bash
# Ver logs de todos os serviços
docker compose logs -f

# Ver logs apenas do bot
docker compose logs -f bot

# Reiniciar apenas o bot
docker compose restart bot

# Parar tudo
docker compose down

# Parar e remover volumes (apaga dados do banco)
docker compose down -v
```

---

## Licença

MIT