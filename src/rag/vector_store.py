import os
import shutil

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.config import HUGGINGFACE_API_KEY, RAG_FILES_DIR, VECTOR_STORE_PATH


def load_documents():
    docs = []
    processed_dir = os.path.join(RAG_FILES_DIR, 'processed')
    os.makedirs(processed_dir, exist_ok=True)

    files = [
        os.path.join(RAG_FILES_DIR, f)
        for f in os.listdir(RAG_FILES_DIR)
        if f.endswith('.txt') or f.endswith('.pdf')
    ]

    for file in files:
        loader = PyPDFLoader(file) if file.endswith('.pdf') else TextLoader(file)

        docs.extend(loader.load())
        # Move o arquivo para 'processed' após indexação para evitar
        # reindexação duplicada nas próximas inicializações do container
        dest_path = os.path.join(processed_dir, os.path.basename(file))
        shutil.move(file, dest_path)

    return docs


# Singleton para evitar recarregamento do índice a cada chamada —
# carregar embeddings e o Chroma do disco é custoso
_vectorstore = None


def get_vectorstore():
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    docs = load_documents()
    embedding = HuggingFaceEndpointEmbeddings(
        huggingfacehub_api_token=HUGGINGFACE_API_KEY,
        repo_id='sentence-transformers/all-MiniLM-L6-v2',
    )
    if docs:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
            )

        split = text_splitter.split_documents(docs)
        _vectorstore = Chroma.from_documents(
            documents=split,
            embedding=embedding,
            persist_directory=VECTOR_STORE_PATH
            )
    else:
        # Nenhum documento novo — carrega o vectorstore já persistido em disco
        _vectorstore = Chroma(embedding_function=embedding,
                              persist_directory=VECTOR_STORE_PATH)
    return _vectorstore
